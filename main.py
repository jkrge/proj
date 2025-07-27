import argparse
import json


def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_template(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def create_message(data, template):
    try:
        return template.format(**data)
    except KeyError as e:
        missing = e.args[0]
        raise KeyError(f"Missing key '{missing}' in JSON data")


def main():
    parser = argparse.ArgumentParser(description="Generate message from JSON and template.")
    parser.add_argument("--data", default="data.json", help="Path to JSON data file")
    parser.add_argument("--template", default="template.txt", help="Path to template file")
    args = parser.parse_args()

    data = load_json(args.data)
    template = load_template(args.template)
    message = create_message(data, template)
    print(message)


if __name__ == "__main__":
    main()
