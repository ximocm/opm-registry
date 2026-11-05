//! Validate and run every native registry pipeline through OPM's actual core.
use std::{env, fs, path::PathBuf, sync::Arc, time::{Duration, Instant}};
use opm_exec::{ExecEvent, ExecutionManager};
use opm_pipeline::IssueSeverity;
use opm_store::{PipelineLibrary, ProjectStore, StepStatus};

fn main() {
    let args: Vec<String> = env::args().collect();
    let registry = PathBuf::from(&args[1]);
    let fixtures = PathBuf::from(&args[2]);
    let work = PathBuf::from(&args[3]);
    let library = PipelineLibrary::new(registry.join("pipelines"));
    for name in library.list() {
        let definition = library.load(&name).expect("native document must load");
        let root = work.join(&name);
        let store = Arc::new(ProjectStore::new());
        store.create_work(&root, &definition).expect("create fresh work folder");
        for entry in fs::read_dir(&fixtures).unwrap() {
            let entry = entry.unwrap();
            fs::copy(entry.path(), root.join("Input").join(entry.file_name())).unwrap();
        }
        let blockers: Vec<_> = store.validate().into_iter()
            .filter(|issue| issue.severity == IssueSeverity::Blocker).collect();
        assert!(blockers.is_empty(), "{name}: {blockers:?}");
        println!("Validated {name}: {} steps, no blockers", definition.pipeline.steps.len());
        let engine = ExecutionManager::new(Arc::clone(&store));
        engine.run_selected().expect("start only after visible validation");
        let deadline = Instant::now() + Duration::from_secs(180);
        loop {
            if Instant::now() >= deadline {
                engine.force_stop();
                panic!("{name}: execution timed out");
            }
            match engine.next_event(Duration::from_millis(100)) {
                Some(ExecEvent::StepFinished { step_id, state }) => {
                    println!("  {step_id}: {:?}", state.status);
                    if state.status != StepStatus::Ok {
                        eprintln!("{}", store.log_content(&step_id));
                    }
                }
                Some(ExecEvent::ExecutionFinished) => break,
                _ => {}
            }
        }
        for step in store.steps() {
            assert_eq!(store.state_of(&step.id).status, StepStatus::Ok, "{name}/{}", step.id);
            assert!(store.is_step_ok(&step.id), "missing output for {name}/{}", step.id);
        }
        let report = root.join("outputs/comparison/multiqc_report.html");
        assert!(fs::metadata(report).unwrap().len() > 100, "empty MultiQC report");
        println!("PASS {name}");
    }
}
