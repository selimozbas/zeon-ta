# Momentum

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/momentum.md)

`zeonta.momentum()` — Raw price change over n bars.

## Ne ölçer

Mümkün olan en yalın momentum okuması: fiyat son n barda kendi biriminde ne kadar hareket etti? Yumuşatma yok, normalizasyon yok — sadece bugünün kapanışı eksi n bar önceki kapanış.

## Formül

```text
Momentum = Kapanış - Kapanış (n periyot önce)
```

## Parametreler

**Gerekli girdiler:** `close`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `10` |

## Döndürdükleri

| Kolon |
| --- |
| `MOM_10` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.momentum(df['close'], length=10).tail(3)
```

```text
date
2024-10-25   -2.2001
2024-10-26   -2.7384
2024-10-27   -2.7623
Name: MOM_10, dtype: float64
```

**Accessor biçimi:** `df.zta.momentum(...)`

## Nasıl okunur

Sıfırın üstü, fiyatın n bar önceye göre daha yüksek olduğunu (yükselen momentum) gösterir; sıfırın altı ise daha düşük olduğunu. Çizginin kendi eğimi — momentumun hızlanıp hızlanmadığı ya da zayıflayıp zayıflamadığı — genelde tek başına sıfır kesişiminden daha bilgilendiricidir.

## Dikkat edilmesi gerekenler

Ham fiyat biriminde ifade edilmesi, enstrümanın fiyat seviyesini bilmeden 2'lik bir Momentum okumasının hiçbir anlam taşımadığı demektir — semboller arasında asla karşılaştırmayın. Semboller arasında ya da fiyat seviyesinin kendisinin çok değiştiği uzun bir geçmişte karşılaştırılabilir bir yüzde gerektiğinde [roc](roc.md) kullanın.

## Kaynak

Formül kaynağı: [https://en.wikipedia.org/wiki/Momentum_(technical_analysis)](https://en.wikipedia.org/wiki/Momentum_(technical_analysis))
