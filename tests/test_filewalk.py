from hasty_coder.filewalk import (
    find_project_root,
    get_nonignored_filepaths,
    load_gitignore_spec_relevant_to_path,
)


def test_load_gitignore_spec_relevant_to_path():
    project_root = find_project_root(__file__)
    ignore_spec = load_gitignore_spec_relevant_to_path(project_root)
    print(ignore_spec)


def test_get_nonignored_filepaths():
    project_root = find_project_root(__file__)
    file_paths = get_nonignored_filepaths(project_root)
    for p in file_paths:
        print(p)
    print("PYTHON FILES")
    file_paths = get_nonignored_filepaths(project_root, extensions=[".py"])
    for p in file_paths:
        print(p)
