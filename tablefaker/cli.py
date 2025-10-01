import argparse
from . import tablefaker
from . import relationships

def main():
    parser = argparse.ArgumentParser(description=get_description())
    parser.add_argument('--config', required=True, help='Config yaml file path')
    parser.add_argument('--file_type', required=False, help='Target file type (csv,json,parquet,excel)')
    parser.add_argument('--target', required=False, help='Target folder/file')
    parser.add_argument('--seed', type=int, required=False, help='Override seed value for deterministic output')
    parser.add_argument('--infer-attrs', type=str, required=False, choices=['true', 'false'], help='Override infer_entity_attrs_by_name (true/false)')
    parser.add_argument('--relationships', action='store_true', required=False, help='Generate relationships YAML file')

    args = parser.parse_args()

    file_type = None
    config_source = None
    target_file_path = None

    if args.config is not None:
        config_source = args.config
    else:
        print("Missing --config parameter. Use --help for more detail.")
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

    if isinstance(config_source, str):
        if args.relationships:
            out = relationships.generate_relationships(config_source, target_file_path)
            print(f"Relationships written to {out}")
        else:
            tablefaker.to_target(file_type, config_source, target_file_path, **kwargs)
    else:
        print("Wrong paramater(s)")
        print(get_description())

def get_description():
    return "more detail: https://github.com/necatiarslan/table-faker/blob/main/README.md "

if __name__ == '__main__':
    main()



