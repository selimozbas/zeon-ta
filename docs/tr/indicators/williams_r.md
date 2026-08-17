# Williams %R

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/williams_r.md)

`zeonta.williams_r()` — Where the close sits inside the recent high-low range, on a 0 to -100 scale.

## Ne ölçer

`stoch` ile aynı aralık-konumu fikri, Larry Williams tarafından bağımsız olarak geliştirilmiş ve önce yayımlanmıştır: kapanışın son dönem yüksek-düşük aralığının neresinde olduğu. Williams sadece ölçeği ters çevirip kaydırmıştır — yumuşatılmamış `%K` için tam olarak `%R = %K - 100` — böylece 0 ile 100 yerine 0 ile -100 arasında okunur.

## Formül

```text
%R = (EnYüksekZirve(n) - Kapanış) / (EnYüksekZirve(n) - EnDüşükDip(n)) x -100
```

## Parametreler

**Gerekli girdiler:** `high`, `low`, `close`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `14` |

## Döndürdükleri

| Kolon |
| --- |
| `WILLR_14` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.williams_r(df['high'], df['low'], df['close'], length=14).tail(3)
```

```text
date
2024-10-25   -71.092379
2024-10-26   -95.248807
2024-10-27   -91.636223
Name: WILLR_14, dtype: float64
```

**Accessor biçimi:** `df.zta.williams_r(...)`

## Nasıl okunur

-20 ile 0 arası geleneksel olarak "aşırı alım", -80 ile -100 arası "aşırı satım" sayılır — `stoch`'un 80/20'sinin tam aynası. -50'nin üstüne çıkış, fiyatın son dönem aralığının üst yarısında işlem gördüğünü; altına iniş ise alt yarısında olduğunu gösterir.

## Dikkat edilmesi gerekenler

Yumuşatılmamış `stoch` eksi 100 ile matematiksel olarak özdeş olduğu için tam olarak aynı zayıflığı devralır: bir trendde doyuma ulaşır, trend sürdüğü sürece 0'a ya da -100'e yapışır ve bu süre boyunca erken dönüş sinyalleri üretir. Uç değerlere göre işlem yapmadan önce bir trend filtresiyle birlikte kullanın.

## Kaynak

Formül kaynağı: [https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/williams-r](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/williams-r)
