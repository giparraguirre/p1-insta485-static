"""Build static HTML site from directory of HTML templates and plain files."""

import pathlib
import json
import shutil
import click
import jinja2


@click.command()
@click.argument("input_dir", nargs=1, type=click.Path(exists=True))
@click.option("-o", "--output", "output_dir", type=click.Path(),
              default="generated_html", help="Output directory.")
@click.option("-v", "--verbose", is_flag=True, help="Print more output.")
def main(input_dir, output_dir, verbose):
    """Templated static website generator."""
    input_dir = pathlib.Path(input_dir)
    output_dir = pathlib.Path(output_dir)

    # Reads configuration file:
    try:
        with (input_dir/"config.json").open() as config_file:
            config_list = json.load(config_file)
    except FileNotFoundError as exc:
        click.echo(
            f"insta485generator error: '{input_dir/"config.json"}' not found"
        )
        raise SystemExit(1) from exc
    except json.JSONDecodeError as exc:
        click.echo(f"insta485generator error: '{input_dir/"config.json"}'")
        click.echo(
            f"{exc.msg}: line {exc.lineno} column {exc.colno} (char {exc.pos})"
        )
        raise SystemExit(1) from exc

    # Sets up template environment:
    if not (input_dir/"templates").is_dir():
        click.echo(
            f"insta485generator error: '{input_dir/"templates"}' not found"
        )
        raise SystemExit(1)
    template_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(input_dir/"templates")),
        autoescape=jinja2.select_autoescape(['html', 'xml']),
    )

    # Creates the output directory:
    if output_dir.exists():
        # Exits with an error message if the output directory already exists:
        click.echo(f"insta485generator error: '{output_dir}' already exists")
        raise SystemExit(1)
    output_dir.mkdir(parents=True)

    for item in config_list:
        # Components from the config file:
        url = item["url"].lstrip("/")  # removes leading slash.
        template_name = item["template"]
        context = item["context"]

        try:
            # Loads the template:
            template = template_env.get_template(template_name)

            # Renders template, providing values from context dictionary:
            rendered_template = template.render(context)
        except jinja2.TemplateError as exc:
            click.echo(f"insta485generator error: '{template_name}'")
            click.echo(str(exc))
            raise SystemExit(1) from exc

        # Given from spec:
        output_path = output_dir/url/"index.html"

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered_template, encoding="utf-8")

        if verbose:
            click.echo(f"Rendered {template_name} -> {output_path}")

    # Copies static/ directory:
    if (input_dir/"static").exists():
        shutil.copytree(input_dir/"static", output_dir, dirs_exist_ok=True)

        if verbose:
            click.echo(f"Copied {input_dir/"static"} -> {output_dir}")


if __name__ == "__main__":
    main()
