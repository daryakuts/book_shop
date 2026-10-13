from sqlalchemy import create_engine, String, Integer, DateTime, Float, ForeignKey, select, func
from sqlalchemy.orm import declarative_base, sessionmaker, Mapped, mapped_column, relationship
from datetime import datetime, timedelta
from config import DB_NAME, DB_USER, DB_PASS, DB_HOST, DB_PORT



DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
# Базовый класс
BaseModel = declarative_base()

# pool_pre_ping - проверка живости соединения
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
Session = sessionmaker(bind=engine)


# 1
class Genre(BaseModel):
    __tablename__ = 'genre'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)

    books: Mapped[list["Book"]] = relationship(back_populates="genre")
    def __repr__(self):
        return f"<Genre(id={self.id}, name='{self.name}')>"


# 2
class Author(BaseModel):
    __tablename__ = 'author'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Связь с книгами (один ко многим)
    books: Mapped[list["Book"]] = relationship(back_populates="author")

    def __repr__(self):
        return f"<Author(id={self.id}, name='{self.name}')>"


# 3
class Book(BaseModel):
    __tablename__ = 'book'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Внешние ключи
    genre_id: Mapped[int] = mapped_column(ForeignKey("genre.id"), nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("author.id"), nullable=False)

    # Связи
    genre: Mapped["Genre"] = relationship(back_populates="books")
    author: Mapped["Author"] = relationship(back_populates="books")

    # Связь с buy_book (многие ко многим через buy_book)
    buy_books: Mapped[list["BuyBook"]] = relationship(back_populates="book")

    def __repr__(self):
        return f"<Book(id={self.id}, title='{self.title}', price={self.price}, stock={self.stock})>"


# 4
class City(BaseModel):
    __tablename__ = 'city'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    delivery_time: Mapped[int] = mapped_column(Integer, nullable=False)  # время доставки в днях

    clients: Mapped[list["Client"]] = relationship(back_populates="city")

    def __repr__(self):
        return f"<City(id={self.id}, name='{self.name}', delivery_time={self.delivery_time})>"


# 5
class Client(BaseModel):
    __tablename__ = 'client'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    city_id: Mapped[int] = mapped_column(ForeignKey("city.id"), nullable=False)

    city: Mapped["City"] = relationship(back_populates="clients")
    buys: Mapped[list["Buy"]] = relationship(back_populates="client")

    def __repr__(self):
        return f"<Client(id={self.id}, name='{self.name}', email='{self.email}')>"


# 6
class Buy(BaseModel):
    __tablename__ = 'buy'

    id: Mapped[int] = mapped_column(primary_key=True)
    wish: Mapped[str] = mapped_column(String(500), nullable=True)

    client_id: Mapped[int] = mapped_column(ForeignKey("client.id"), nullable=False)

    client: Mapped["Client"] = relationship(back_populates="buys")
    buy_books: Mapped[list["BuyBook"]] = relationship(back_populates="buy")
    buy_steps: Mapped[list["BuyStep"]] = relationship(back_populates="buy")

    def __repr__(self):
        return f"<Buy(id={self.id}, client_id={self.client_id}, wish='{self.wish}')>"


# 7
class BuyBook(BaseModel):
    __tablename__ = 'buy_book'

    id: Mapped[int] = mapped_column(primary_key=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    book_id: Mapped[int] = mapped_column(ForeignKey("book.id"), nullable=False)
    buy_id: Mapped[int] = mapped_column(ForeignKey("buy.id"), nullable=False)

    book: Mapped["Book"] = relationship(back_populates="buy_books")
    buy: Mapped["Buy"] = relationship(back_populates="buy_books")

    def __repr__(self):
        return f"<BuyBook(id={self.id}, book_id={self.book_id}, buy_id={self.buy_id}, quantity={self.quantity})>"


# 8
class Step(BaseModel):
    __tablename__ = 'step'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)

    buy_steps: Mapped[list["BuyStep"]] = relationship(back_populates="step")

    def __repr__(self):
        return f"<Step(id={self.id}, name='{self.name}')>"


# 9
class BuyStep(BaseModel):
    __tablename__ = 'buy_step'

    id: Mapped[int] = mapped_column(primary_key=True)
    date_start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    date_end: Mapped[datetime] = mapped_column(DateTime, nullable=True)  # может быть NULL, если этап не завершён

    buy_id: Mapped[int] = mapped_column(ForeignKey("buy.id"), nullable=False)
    step_id: Mapped[int] = mapped_column(ForeignKey("step.id"), nullable=False)

    buy: Mapped["Buy"] = relationship(back_populates="buy_steps")
    step: Mapped["Step"] = relationship(back_populates="buy_steps")

    def __repr__(self):
        return f"<BuyStep(id={self.id}, buy_id={self.buy_id}, step_id={self.step_id}, start={self.date_start}, end={self.date_end})>"


BaseModel.metadata.drop_all(engine)
print("Все таблицы удалены")

BaseModel.metadata.create_all(engine)
print("Таблицы созданы заново")

session = Session()

genres = [
    Genre(name="Роман"),
    Genre(name="Детектив"),
    Genre(name="Фантастика"),
    Genre(name="Комедия"),
]
session.add_all(genres)
session.commit()
print("Жанры добавлены")

authors = [
    Author(name="Лев Толстой"),
    Author(name="Фёдор Достоевский"),
    Author(name="Михаил Булгаков"),
    Author(name="Артур Конан Дойл"),
    Author(name="Агата Кристи"),
]
session.add_all(authors)
session.commit()
print("Авторы добавлены")

books = [
    Book(title="Война и мир", price=500.0, stock=10, genre_id=1, author_id=1),
    Book(title="Преступление и наказание", price=400.0, stock=5, genre_id=1, author_id=2),
    Book(title="Мастер и Маргарита", price=600.0, stock=7, genre_id=1, author_id=3),
    Book(title="Собака Баскервилей", price=350.0, stock=8, genre_id=2, author_id=4),
    Book(title="Убийство в Восточном экспрессе", price=450.0, stock=6, genre_id=2, author_id=5),
    Book(title="Автостопом по галактике", price=550.0, stock=4, genre_id=3, author_id=3),
]
session.add_all(books)
session.commit()
print("Книги добавлены")

cities = [
    City(name="Москва", delivery_time=1),
    City(name="Санкт-Петербург", delivery_time=2),
    City(name="Казань", delivery_time=3),
    City(name="Новосибирск", delivery_time=5),
]
session.add_all(cities)
session.commit()
print("Города добавлены")


clients = [
    Client(name="Анна Иванова", email="anna@mail.ru", city_id=1),
    Client(name="Пётр Петров", email="petr@mail.ru", city_id=2),
    Client(name="Мария Смирнова", email="maria@mail.ru", city_id=1),
    Client(name="Иван Сидоров", email="ivan@mail.ru", city_id=3),
]
session.add_all(clients)
session.commit()
print("Клиенты добавлены")

buys = [
    Buy(wish="Быстрая доставка", client_id=1),
    Buy(wish="Упаковать в плёнку", client_id=2),
    Buy(wish=None, client_id=3),
    Buy(wish="Подарочная упаковка", client_id=1),
]
session.add_all(buys)
session.commit()
print("Заказы добавлены")

buy_books = [
    BuyBook(quantity=2, book_id=1, buy_id=1),
    BuyBook(quantity=1, book_id=3, buy_id=1),
    BuyBook(quantity=3, book_id=2, buy_id=2),
    BuyBook(quantity=1, book_id=4, buy_id=3),
    BuyBook(quantity=2, book_id=5, buy_id=3),
    BuyBook(quantity=1, book_id=6, buy_id=4),
]
session.add_all(buy_books)
session.commit()
print("Связи книг с заказами добавлены")

steps = [
    Step(name="Оформлен"),
    Step(name="Оплачен"),
    Step(name="Собран"),
    Step(name="Доставлен"),
    Step(name="Завершён"),
]
session.add_all(steps)
session.commit()
print("Этапы добавлены")


now = datetime.now()
buy_steps = [
    BuyStep(date_start=now, date_end=now + timedelta(hours=1), buy_id=1, step_id=1),
    BuyStep(date_start=now + timedelta(hours=1), date_end=now + timedelta(hours=3), buy_id=1, step_id=2),
    BuyStep(date_start=now + timedelta(hours=3), date_end=None, buy_id=1, step_id=3),

    BuyStep(date_start=now, date_end=now + timedelta(hours=2), buy_id=2, step_id=1),
    BuyStep(date_start=now + timedelta(hours=2), date_end=now + timedelta(hours=5), buy_id=2, step_id=2),

    BuyStep(date_start=now, date_end=now + timedelta(hours=1), buy_id=3, step_id=1),
    BuyStep(date_start=now + timedelta(hours=1), date_end=None, buy_id=3, step_id=4),

    BuyStep(date_start=now, date_end=None, buy_id=4, step_id=1),
]
session.add_all(buy_steps)
session.commit()
session.close()
print("Тестовые данные добавлены")

# ЗАПРОСЫ
session = Session()

print("запрос1 : Книги жанра 'Роман' с авторами")

stmt = select(Book).join(Genre).where(Genre.name == "Роман")
romance_books = session.scalars(stmt).all()
for book in romance_books:
    print(f"{book.title}")
    print(f"Автор: {book.author.name}")
    print(f"Цена: {book.price} руб.")
    print(f"В наличии: {book.stock} шт.")


print("запрос 2: Заказы клиента 'Анна Иванова'")
stmt = select(Client).where(Client.name == "Анна Иванова")
client = session.scalars(stmt).first()
if client:
    print(f"Клиент: {client.name} ({client.email})")
    print(f"Город: {client.city.name}")
    print(f"Время доставки: {client.city.delivery_time} дн.")

    for buy in client.buys:
        print(f"Заказ #{buy.id}")
        print(f"Пожелания: {buy.wish or 'нет'}")
        total = 0
        for buy_book in buy.buy_books:
            book = buy_book.book
            subtotal = book.price * buy_book.quantity
            total += subtotal
            print(f"{book.title} x{buy_book.quantity} = {subtotal} руб.")
        print(f"Итого: {total} руб.")
else:
    print("Клиент не найден")


print("запрос 3: Этапы заказа #1")
stmt = select(Buy).where(Buy.id == 1)
buy = session.scalars(stmt).first()
if buy:
    print(f"Заказ #{buy.id}, клиент: {buy.client.name}")
    print(f"Пожелания: {buy.wish or 'нет'}")
    print()
    print("Этапы:")
    for buy_step in buy.buy_steps:
        status = "в процессе" if buy_step.date_end is None else f"завершён {buy_step.date_end.strftime('%d.%m.%Y %H:%M')}"
        print(f"{buy_step.step.name}: начат {buy_step.date_start.strftime('%d.%m.%Y %H:%M')} - {status}")
    print()
else:
    print("Заказ #1 не найден")


print("запрос 4: Книги с остатком меньше 10 штук")
stmt = select(Book).where(Book.stock < 10)
books = session.scalars(stmt).all()
for book in books:
    print(f"{book.title}: {book.stock} шт. (автор: {book.author.name})")


print("запрос 5: Книги жанра 'Детектив' со связями (дополнительный)")
stmt = select(Book).join(Genre).where(Genre.name =="Детектив")
detective_books = session.scalars(stmt).all()
for book in detective_books:
    print(f"{book.title} ({book.author.name}) - {book.price} руб.")
    # есть ли заказы на эту книгу
    orders_count = len(book.buy_books)
    print(f"Заказов: {orders_count}")

session.close()
print("Все запросы выполнены!")