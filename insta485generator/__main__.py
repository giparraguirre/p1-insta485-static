"""Build static HTML site from directory of HTML templates and plain files."""

import click
import pathlib
import json
import jinja2

@click.command()
@click.argument("input_dir", nargs=1, type=click.Path(exists=True))
@click.option("-o", "--output", "output_dir", type=click.Path(), default="generated_html")
def main(input_dir, output_dir):
    input_dir = pathlib.Path(input_dir)
    output_dir = pathlib.Path(output_dir)

    # Reads configuration file:
    config_filename = input_dir/"config.json"
    with config_filename.open() as config_file:
        config_list = json.load(config_file)

    # Sets up template environment:
    template_dir = input_dir/"templates"
    template_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(template_dir)),
        autoescape=jinja2.select_autoescape(['html', 'xml']),
    )

    # Creates the output directory, exiting with an error message if the output directory already exists:
    if output_dir.exists():
        raise FileExistsError(f"Output directory '{output_dir}' already exists.")
    output_dir.mkdir(parents=True)

    for item in config_list:
        # Components from the config file:
        url = item["url"].lstrip("/") # removes leading slash.
        template_name = item["template"]
        context = item["context"]

        # Loads the template: 
        template = template_env.get_template(template_name)

        # Renders template, providing values from context dictionary:
        rendered_template = template.render(context)

        # Given from spec:
        output_path = output_dir/url/"index.html"

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered_template, encoding="utf-8")

    print(f"DEBUG input_dir={input_dir}")

if __name__ == "__main__":
    main()
