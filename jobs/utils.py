from typing import Iterable
from matplotlib.figure import Figure
import base64
from io import BytesIO


def online_average(xs: Iterable[float]):
    _sum = 0.0
    _cnt = 0
    for x in xs:
        _sum += x
        _cnt += 1

    if _cnt == 0:
        return 0
    return _sum / _cnt


def base64img(fig: Figure):
    buffer = BytesIO()
    fig.savefig(buffer, format="jpg")
    buffer.seek(0)
    encoded = base64.b64encode(buffer.read()).decode("utf-8")
    data_url = f"data:image/jpeg;base64,{encoded}"
    return data_url