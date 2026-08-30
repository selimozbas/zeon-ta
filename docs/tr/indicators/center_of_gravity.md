# Ağırlık Merkezi Osilatörü (CG)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/center_of_gravity.md)

`zeonta.center_of_gravity()` — Ehlers' zero-lag oscillator: the balance point of price over the window.

## Ne ölçer

John Ehlers'ın denge noktası osilatörü: pencerenin fiyatlarını bir kirişin üzerindeki ağırlıklar olarak ele alır ve nerede dengeleneceğini bulur, sonra işaretini ters çevirir çünkü o denge noktası fiyat salınımlarının tam tersi yönde hareket eder. Sonuç, gecikme karşılığında pürüzsüzlük veren geleneksel bir düzleştirilmiş indikatörün aksine, esasen sıfır gecikmeli, düzleştirilmiş bir osilatördür.

## Formül

```text
Fiyat = (Yüksek+Düşük)/2; CG = -toplam((1+k)*Fiyat[t-k], k=0..n-1) / toplam(Fiyat[t-k], k=0..n-1)
```

## Parametreler

**Gerekli girdiler:** `high`, `low`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `10` |

## Döndürdükleri

| Kolon |
| --- |
| `CG_10` |
| `CGs_10` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.center_of_gravity(df['high'], df['low']).tail(3)
```

```text
               CG_10    CGs_10
date                          
2024-10-25 -5.518245 -5.520843
2024-10-26 -5.514617 -5.518245
2024-10-27 -5.515026 -5.514617
```

**Accessor biçimi:** `df.zta.center_of_gravity(...)`

## Nasıl okunur

Ehlers'in kendi önerdiği sinyal, CG ile kendi bir-bar-gecikmeli tetik çizgisi arasındaki kesişimdir — [fisher_transform](fisher_transform.md)'ın kullandığı aynı desen. İdeal olarak, `length` piyasanın baskın döngü uzunluğunun yaklaşık yarısı olmalıdır.

## Dikkat edilmesi gerekenler

Ölçek, farklı `length` değerleri arasında ya da fiyatın kendisiyle karşılaştırılabilir değildir — Ehlers'in kendi makalesi yalnızca eğrinin *şeklinin* önemli olduğunu belirtir.

## Kaynak

Formül kaynağı: [https://www.mesasoftware.com/papers/TheCGOscillator.pdf](https://www.mesasoftware.com/papers/TheCGOscillator.pdf)
