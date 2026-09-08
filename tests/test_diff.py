from ai_actions.diff import count_changes, render_word_diff_html


def test_no_changes():
    text = "No changes here."
    assert count_changes(text, text) == 0
    assert render_word_diff_html(text, text) == text


def test_empty_strings():
    assert count_changes("", "") == 0
    assert render_word_diff_html("", "") == ""


def test_single_word_replacement_is_spaced_correctly():
    # Locks in the exact output verified by hand during Phase 2: without
    # the spacing fix, "are"/"is" render glued together as "areis".
    html = render_word_diff_html("This are a test.", "This is a test.")
    assert html == (
        'This <span style="color:#c0392b; text-decoration:line-through;">are</span> '
        '<span style="color:#1e7e34; text-decoration:underline;">is</span> a test.'
    )
    assert count_changes("This are a test.", "This is a test.") == 1


def test_pure_insertion_has_no_deletion_span():
    original = "Extra word here"
    revised = "Extra word is here now"
    html = render_word_diff_html(original, revised)
    assert count_changes(original, revised) == 2
    assert "line-through" not in html
    assert html.count("underline") == 2


def test_pure_deletion_has_no_insertion_span():
    original = "Remove this word entirely"
    revised = "Remove word entirely"
    html = render_word_diff_html(original, revised)
    assert count_changes(original, revised) == 1
    assert "line-through" in html
    assert "underline" not in html


def test_html_special_characters_are_escaped():
    html = render_word_diff_html("a < b & c", "a < b & d")
    assert "&lt;" in html
    assert "&amp;" in html
    assert "<b>" not in html
