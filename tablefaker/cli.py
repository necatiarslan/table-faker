import argparse
from . import tablefaker
from . import relationships
from . import semantic_view
# from . import semantic_view_enhanced
from . import semantic_model_metrics

def main():
    parser = argparse.ArgumentParser(description=get_description())
    parser.add_argument('--config', required=False, help='Config yaml file path (required for data generation, relationships, and semantic views)')
    parser.add_argument('--file_type', required=False, help='Target file type (csv,json,parquet,excel)')
    parser.add_argument('--target', required=False, help='Target folder/file')
    parser.add_argument('--seed', type=int, required=False, help='Override seed value for deterministic output')
    parser.add_argument('--infer-attrs', type=str, required=False, choices=['true', 'false'], help='Override infer_entity_attrs_by_name (true/false)')
    parser.add_argument('--relationships', action='store_true', required=False, help='Generate relationships YAML file')
    parser.add_argument('--semantic-view', action='store_true', required=False, help='Generate semantic view YAML file')
    # parser.add_argument('--semantic-view-enhanced', action='store_true', required=False, help='Generate enhanced semantic view with split files and caching')
    parser.add_argument('--generate-metrics', required=False, help='Generate business metrics from semantic view YAML file')
    parser.add_argument('--num-metrics', type=int, default=10, required=False, help='Number of metrics to generate (default: 10)')
    parser.add_argument('--llm-config', required=False, help='Path to LLM config file (default: llm.config in current dir)')

    args = parser.parse_args()

    file_type = None
    config_source = None
    target_file_path = None

    # Check if --generate-metrics is being used (doesn't require --config)
    if hasattr(args, 'generate_metrics') and args.generate_metrics:
        # --generate-metrics doesn't need --config
        pass
    elif args.config is not None:
        config_source = args.config
    else:
        print("Missing --config parameter. Use --help for more detail.")
        print("Note: --generate-metrics does not require --config")
        return

    if args.file_type is not None:
        file_type = args.file_type
    else:
        file_type = "csv"

    if args.target is not None:
        target_file_path = args.target
    else:
        target_file_path = "."  


    # Prepare kwargs for overriding config values
    kwargs = {}
    if args.seed is not None:
        kwargs['seed'] = args.seed
    if hasattr(args, 'infer_attrs') and args.infer_attrs is not None:
        kwargs['infer_attrs'] = args.infer_attrs

    # Handle generate-metrics separately as it takes a semantic view file, not config
    if hasattr(args, 'generate_metrics') and args.generate_metrics:
        llm_config = args.llm_config if hasattr(args, 'llm_config') else None
        num_metrics = args.num_metrics if hasattr(args, 'num_metrics') else 10
        out = semantic_model_metrics.generate_model_metrics(
            args.generate_metrics,
            llm_config,
            num_metrics,
            target_file_path
        )
        print(f"Generated {num_metrics} business metrics written to {out}")
    elif isinstance(config_source, str):
        if args.relationships:
            out = relationships.generate_relationships(config_source, target_file_path)
            print(f"Relationships written to {out}")
        # elif hasattr(args, 'semantic_view_enhanced') and args.semantic_view_enhanced:
        #     llm_config = args.llm_config if hasattr(args, 'llm_config') else None
        #     out_files = semantic_view_enhanced.generate_semantic_view_enhanced(config_source, target_file_path, llm_config)
        #     print(f"Enhanced semantic view files generated:")
        #     for file_type, file_path in out_files.items():
        #         print(f"  - {file_type}: {file_path}")
        elif hasattr(args, 'semantic_view') and args.semantic_view:
            llm_config = args.llm_config if hasattr(args, 'llm_config') else None
            out = semantic_view.generate_semantic_view(config_source, target_file_path, llm_config)
            print(f"Semantic view written to {out}")
        else:
            tablefaker.to_target(file_type, config_source, target_file_path, **kwargs)
    else:
        print("Wrong paramater(s)")
        print(get_description())

def get_description():
    return "more detail: https://github.com/necatiarslan/table-faker/blob/main/README.md "

if __name__ == '__main__':
    main()



