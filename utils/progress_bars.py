from rich.console import Group
from rich.live import Live
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn, TaskProgressColumn
from rich.rule import Rule
from rich.console import Console

label_progress = Progress(
    TimeElapsedColumn(),
    TextColumn('{task.description}'),
)

# progress for a task step that takes a while, but we're not sure how long
step_progress_timed = Progress(
    TextColumn('\t'),
    TimeElapsedColumn(),
    TextColumn('[bold blue]{task.fields[action]}'),
    SpinnerColumn('simpleDots')
)

# progress for a task step that has a known total target (steps, ...)
step_progress = Progress(
    TextColumn('\t'),
    TimeElapsedColumn(),
    TextColumn('[bold blue]{task.fields[action]}'),
    BarColumn(),
    TextColumn('({task.completed}/{task.total})')
)

overall_progress = Progress(
    TimeElapsedColumn(),
    BarColumn(),
    TextColumn('{task.description}'),
    TaskProgressColumn(),
    SpinnerColumn('simpleDots')
)

group = Group(
    label_progress,
    step_progress_timed,
    Rule(style='#AAAAAA'),
    overall_progress
)


def set_progress_bar(known_amount: bool = False):
    def progress_bar_decorator(func):
        def collect_data_from_links(*args, **kwargs):
            overall_task_id = overall_progress.add_task('', total=2)
            progress_gen = func(*args, **kwargs)
            with Live(group):
                page_counter = 0
                try:
                    while True:
                        overall_progress.update(overall_task_id, description="[bold blue]Data collection from links")
                        label_task_id = label_progress.add_task(f"Page number "
                                                                f"[bold blue]{page_counter + 1}[/bold blue]")
                        step_task_id = step_progress_timed.add_task('', action="Collecting data from page")

                        yield next(progress_gen)
                        page_counter += 1

                        step_progress_timed.update(step_task_id, advance=1)
                        step_progress_timed.stop_task(step_task_id)
                        step_progress_timed.update(step_task_id, visible=False)

                        label_progress.stop_task(label_task_id)
                        label_progress.update(label_task_id, description=f"[green]Data from page "
                                                                         f"[bold blue]{page_counter}[/bold blue] "
                                                                         f"has been collected.")
                        overall_progress.update(overall_task_id, advance=1)
                except StopIteration:
                    label_progress.update(label_task_id, visible=False)
                    step_progress_timed.update(step_task_id, visible=False)
                    overall_progress.update(overall_task_id, description=f"[green]All data from "
                                                                         f"[bold blue]{page_counter}[/bold blue] pages "
                                                                         f"has been collected!")

        def collect_data_by_click_next_page(*args, **kwargs):
            console = Console()
            progress_gen = func(*args, **kwargs)
            with console.status("[bold blue]Collecting data by click 'next_page'..."):
                page_counter = 0
                try:
                    while True:
                        yield next(progress_gen)
                        page_counter += 1
                        console.log(f"[green]Finish Collecting data from page[/green] {page_counter}")

                except StopIteration:
                    console.log(f"[bold][green]All data from [bold][blue]{page_counter}[/blue] "
                                f"pages successfully collected!")

        return collect_data_from_links if known_amount else collect_data_by_click_next_page

    return progress_bar_decorator
