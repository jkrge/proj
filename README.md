# JSON Message Generator

This project reads a JSON file and uses a text template to generate a message.

## Usage

Run the script with optional `--data` and `--template` arguments:

```bash
python main.py --data path/to/data.json --template path/to/template.txt
```

By default it uses `data.json` and `template.txt` in the project root.

The template should use Python's `str.format` syntax with keys matching the JSON fields.

Example `data.json`:

```json
{
  "name": "Alice",
  "balance": 250.75
}
```

Example `template.txt`:

```
Hello, {name}! Your balance is ${balance}.
```

Running the script will output:

```
Hello, Alice! Your balance is $250.75.
```
