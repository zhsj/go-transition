if __name__ == "__main__":
    # import usercustomize  # noqa
    from go_transition import build_db, render
    import sqlite3

    conn = sqlite3.connect(":memory:")
    mirror = "mirrors.tuna.tsinghua.edu.cn"
    build_db.build_db(conn, mirror)
    render.render(conn)
