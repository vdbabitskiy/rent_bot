from dataclasses import dataclass
from typing import List


@dataclass
class Advertisement:
    title: str
    time: str
    type: str
    description: str
    link: str
    price: str
    location: str
    images: List[str]

    def to_dict(self):
        return {
            'title': self.title,
            'time': self.time,
            'type': self.type,
            'description': self.description,
            'link': self.link,
            'price': self.price,
            'location': self.location,
            'images': self.images
        }

    def __str__(self):
        return f'<b>❇️{self.title}</b>\n\n<b>💰{self.price}</b>\n\n\n<i>{self.description}</i>\n\n📍{self.location}\n({self.time})\n\n➡️ <a href="{self.link}">Объявление</a>'
