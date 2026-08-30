# Kaufman Verimlilik Oranı (ER)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/efficiency_ratio.md)

`zeonta.efficiency_ratio()` — How efficiently price is trending: net movement over total movement.

## Ne ölçer

[kama](kama.md)'nın kendi düzleştirme sabitine harmanladığı uyarlanabilir çekirdek, burada tek başına sunulur: net hareket bölü toplam hareket — bir pencerenin bar-başı çalkantısının ne kadarının gerçekten bir yere vardığının doğrudan bir ölçüsü.

## Formül

```text
ER = |Kapanış - Kapanış[n önce]| / Toplam(|Kapanış[i] - Kapanış[i-1]|, n)
```

## Parametreler

**Gerekli girdiler:** `close`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `10` |

## Döndürdükleri

| Kolon |
| --- |
| `ER_10` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.efficiency_ratio(df['close']).tail(3)
```

```text
date
2024-10-25    0.434691
2024-10-26    0.489035
2024-10-27    0.491207
Name: ER_10, dtype: float64
```

**Accessor biçimi:** `df.zta.efficiency_ratio(...)`

## Nasıl okunur

`1`, pencerenin düz bir çizgide trend yaptığı; `0`'a yakın ise yerinde çalkalandığı anlamına gelir. `kama`'nın dahili olarak kullandığı gibi, doğrudan işlem yapmak yerine genellikle başka bir indikatörün parametrelerine beslenen bir rejim filtresi olarak kullanılır.

## Dikkat edilmesi gerekenler

Tamamen düz bir pencerede tanımsız bir `0/0` yerine `0` olur.

## Kaynak

Formül kaynağı: [https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/kaufmans-adaptive-moving-average-kama](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/kaufmans-adaptive-moving-average-kama)
