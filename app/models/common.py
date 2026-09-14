from decimal import Decimal
from typing import Annotated

from pydantic import PlainSerializer

MoneyDecimal = Annotated[Decimal, PlainSerializer(lambda value: str(value), return_type=str, when_used="json")]
