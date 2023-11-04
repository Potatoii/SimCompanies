from sqlalchemy import create_engine

import settings

engine = create_engine(f"sqlite:///{settings.root_path}/database/SimCompanies.db")


def select_example():
    """
    查询示例
    """
    from sqlalchemy import text
    from sqlalchemy.orm import sessionmaker

    session_func = sessionmaker(bind=engine)
    db_session = session_func()
    # 执行查询
    result = db_session.execute(text("SELECT * FROM item"))  # noqa

    # 打印查询结果
    for row in result:
        print(row)


if __name__ == "__main__":
    select_example()
