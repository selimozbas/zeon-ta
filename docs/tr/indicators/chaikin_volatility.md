# Chaikin Oynaklığı (CVI)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/chaikin_volatility.md)

`zeonta.chaikin_volatility()` — Rate of change of a smoothed high-low range: is the range widening or narrowing.

## Ne ölçer

Marc Chaikin'in oynaklığa değişim-oranı yaklaşımı: [atr](atr.md)'nin yaptığı gibi tipik aralığı bir seviye olarak bildirmek yerine, bu aralığı bir EMA ile yumuşatır ve ardından o yumuşatılmış aralığın aynı pencere üzerindeki *yüzde değişimini* bildirir — aralığın şu anda ne kadar büyük olduğu değil, genişleyip daralmadığı.

## Formül

```text
CVI = ROC(EMA(Yüksek - Düşük, n), n)
```

## Parametreler

**Gerekli girdiler:** `high`, `low`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `10` |

## Döndürdükleri

| Kolon |
| --- |
| `CVI_10` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.chaikin_volatility(df['high'], df['low']).tail(3)
```

```text
date
2024-10-25     4.441483
2024-10-26    -6.330787
2024-10-27   -12.577711
Name: CVI_10, dtype: float64
```

**Accessor biçimi:** `df.zta.chaikin_volatility(...)`

## Nasıl okunur

Pozitif olması, aralığın pencere boyunca genişlediği (oynaklığın arttığı) anlamına gelir; negatif olması ise daraldığı (oynaklığın yatıştığı) anlamına gelir — genellikle düşük, düşmekte olan bir CVI'nin öncülük edebileceği fırtına-öncesi-sessizlik kurulumunu tespit etmek için kullanılır.

## Dikkat edilmesi gerekenler

Zaten yumuşatılmış bir niceliğin değişim oranı — `atr`'nin kendisinden daha fazla gecikme bekleyin, çünkü bu, EMA yumuşatmasının üzerine ikinci bir dönüşüm daha ekler.

## Kaynak

Formül kaynağı: [https://www.luxalgo.com/library/concept/chaikin-volatility/](https://www.luxalgo.com/library/concept/chaikin-volatility/)
