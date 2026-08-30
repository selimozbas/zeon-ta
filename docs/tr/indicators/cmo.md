# Chande Momentum Osilatörü (CMO)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/cmo.md)

`zeonta.cmo()` — Sum of gains vs. losses over a plain window, unlike RSI's Wilder smoothing.

## Ne ölçer

[rsi](rsi.md) ile aynı yukarı-hareket/aşağı-hareket ayrımından inşa edilir, ama farklı birleştirilir (bir oran yerine normalize edilmiş bir fark) ve RSI'ın aksine hiç yumuşatılmaz — bir kazanç ya da kayıp, `length` barı geçtikten sonra Wilder yumuşatmasının yaptığı gibi kademeli olarak sönmek yerine pencereden tamamen düşer.

## Formül

```text
CMO = 100 * (ArtışToplamı(n) - DüşüşToplamı(n)) / (ArtışToplamı(n) + DüşüşToplamı(n))
```

## Parametreler

**Gerekli girdiler:** `close`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `14` |

## Döndürdükleri

| Kolon |
| --- |
| `CMO_14` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.cmo(df['close']).tail(3)
```

```text
date
2024-10-25   -15.862131
2024-10-26   -25.918211
2024-10-27   -32.165313
Name: CMO_14, dtype: float64
```

**Accessor biçimi:** `df.zta.cmo(...)`

## Nasıl okunur

Diğer sınırlı osilatörlerle aynı -100/+100 ölçeğinde ve aynı aşırı-alım/aşırı-satım sezgisiyle okunur, ama hiç yumuşatılmadığı için, eski bir uç hareketin nihayet pencereden düşmesine RSI'dan daha ani tepki verir.

## Dikkat edilmesi gerekenler

Tamamen düz bir pencerede (her iki toplam da `0`) tanımsız bir `0/0` değil, `0` olur.

## Kaynak

Formül kaynağı: [https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/cmo](https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/cmo)
