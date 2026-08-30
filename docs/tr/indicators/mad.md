# Medyan Mutlak Sapma (MAD)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/mad.md)

`zeonta.mad()` — Rolling median absolute deviation: a spread measure robust to outliers.

## Ne ölçer

[stddev](stddev.md) gibi bir yayılım ölçüsü, ama her adımda ortalama ve kare yerine medyan kullanılarak inşa edilmiştir — ortalama yerine medyan kullanmanın ardındaki aykırı-değerlere-dayanıklılık fikrinin, iki kez uygulanmış hali.

## Formül

```text
MAD = medyan(|Kapanış - medyan(Kapanış, n)|, n)
```

## Parametreler

**Gerekli girdiler:** `close`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `20` |

## Döndürdükleri

| Kolon |
| --- |
| `MAD_20` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.mad(df['close']).tail(3)
```

```text
date
2024-10-25    0.45280
2024-10-26    0.52970
2024-10-27    0.62205
Name: MAD_20, dtype: float64
```

**Accessor biçimi:** `df.zta.mad(...)`

## Nasıl okunur

`stddev` ile aynı yönde okunur — yükselmesi pencerenin daha çalkantılı hale geldiği anlamına gelir — ama tek bir vahşi bar MAD'ı neredeyse hiç oynatmazken, `stddev`'e doğrudan hakim olabilir.

## Dikkat edilmesi gerekenler

Benzer isme rağmen, [cci](cci.md)'nin dahili olarak kullandığı ortalama mutlak sapma ile aynı şey değildir — o, sapmaların ortalamasını alır, bu ise medyanını alır, ve pencerede herhangi bir aykırı değer olduğunda ikisi anlaşmaz.

## Kaynak

Formül kaynağı: [https://en.wikipedia.org/wiki/Median_absolute_deviation](https://en.wikipedia.org/wiki/Median_absolute_deviation)
