# Varyans

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/variance.md)

`zeonta.variance()` — Rolling variance of price.

## Ne ölçer

Kare köke girmeden önceki [stddev](stddev.md) — burada onu karesini alarak değil doğrudan hesaplanır, ama sayısal olarak aynı ilişkidir. İstatistiksel çalışmalar bu biçime yönelir (varyans, bağımsız seriler için toplanabilirdir; standart sapma değildir); grafik çizimi ise fiyatla aynı birimi paylaştığı için `stddev`'e yönelir.

## Formül

```text
VAR = varyans(Kapanış, n) = STDDEV(Kapanış, n) ^ 2
```

## Parametreler

**Gerekli girdiler:** `close`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `20` |
| `ddof` | `0` |

## Döndürdükleri

| Kolon |
| --- |
| `VAR_20` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.variance(df['close']).tail(3)
```

```text
date
2024-10-25    0.518750
2024-10-26    0.638083
2024-10-27    0.849690
Name: VAR_20, dtype: float64
```

**Accessor biçimi:** `df.zta.variance(...)`

## Nasıl okunur

`stddev` ile aynı yön, sadece karesi alınmış (dolayısıyla daha büyük) bir ölçekte.

## Dikkat edilmesi gerekenler

Karesi alınmış birimler — dolar cinsinden bir fiyat serisi için 4 varyans, teknik olarak 'dolar kare'dir, `stddev`'in yaptığı gibi doğrudan fiyatla karşılaştırılamaz.

## Kaynak

Formül kaynağı: [https://en.wikipedia.org/wiki/Variance](https://en.wikipedia.org/wiki/Variance)
