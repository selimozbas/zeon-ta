# McGinley Dinamik

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/mcgd.md)

`zeonta.mcgd()` — A moving average that speeds up in fast markets and slows down in quiet ones.

## Ne ölçer

John McGinley bunu, sıradan hareketli ortalamalar hakkındaki özel bir şikayeti gidermek için geliştirdi: sabit periyotlu bir EMA/SMA, hızlı bir piyasada kötü gecikir ve yavaş bir piyasada yalancı sinyaller verir, çünkü hızı hiç değişmez. `(Kapanış/MD)^4` terimi, McGinley Dinamik'i bunun yerine kendi kendine ayarlanır hale getirir — fiyat kendisinden her uzaklaştığında otomatik olarak hızlanır, fiyat ve ortalama tekrar yakınlaştığında yavaşlar.

## Formül

```text
MD[0] = Kapanış[0]; MD[i] = MD[i-1] + (Kapanış[i] - MD[i-1]) / (N * (Kapanış[i]/MD[i-1])^4), N = length
```

## Parametreler

**Gerekli girdiler:** `close`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `10` |

## Döndürdükleri

| Kolon |
| --- |
| `MCGD_10` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.mcgd(df['close']).tail(3)
```

```text
date
2024-10-25    90.661309
2024-10-26    90.496121
2024-10-27    90.275758
Name: MCGD_10, dtype: float64
```

**Accessor biçimi:** `df.zta.mcgd(...)`

## Nasıl okunur

Herhangi bir hareketli ortalama gibi okunur (fiyatın üstünden geçmesi, kendi eğimi) — McGinley'nin kendi savı, farklı okunması değil, değişen piyasa koşulları boyunca sabit periyotlu bir EMA/SMA'nın ihtiyaç duyacağından daha az yeniden ayara ihtiyaç duymasıdır.

## Dikkat edilmesi gerekenler

`Kapanış` `0` olduğunda `(Kapanış/MD)^4` terimi tam olarak `0` olur, bu da güncelleme adımında sıfıra bölüme yol açar — bu tekil noktada formülün gerçek bir cevabı olmadığı için, o bar için önceki değerde tutulur.

## Kaynak

Formül kaynağı: [https://www.tradingview.com/support/solutions/43000589175-mcginley-dynamic/](https://www.tradingview.com/support/solutions/43000589175-mcginley-dynamic/)
