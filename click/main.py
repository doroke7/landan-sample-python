import click


@click.group()
def cli():
    pass


@cli.command()
def start():
    click.echo("start server")


@cli.command()
def stop():
    click.echo("stop server")


if __name__ == "__main__":
    cli()