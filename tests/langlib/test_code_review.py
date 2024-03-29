from hasty_coder.tasklib.code_review import review_path


def test_code_review():
    project_root = "/Users/bryce/projects/hasty-coder"
    for snippet, comments in review_path(project_root):
        print(f"Checked {snippet.filepath}:{snippet.start_line}")
        for line_no, comment in comments:
            lint_line = f"{snippet.filepath}:{line_no} - {comment}"
            print(lint_line)
