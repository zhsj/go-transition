if __name__ == "__main__":
    # import usercustomize  # noqa
    from go_transition import build_db, render
    import sqlite3

    conn = sqlite3.connect(":memory:")
    build_db.main(conn)
    render.main(conn)
