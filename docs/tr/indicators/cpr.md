# Merkezi Pivot Aralığı (CPR)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/cpr.md)

`zeonta.cpr()` — Classic pivot with a width band (Top/Bottom Central) around it, from the prior bar.

## Ne ölçer

[pivot_points](pivot_points.md)'un hesapladığı aynı klasik pivot, artı aynı önceki barın aralığından oluşturulan bir genişlik bandı (Alt Merkez, Üst Merkez). Bandın genişliği her zaman tam olarak önceki kapanış ile önceki aralığın orta noktası arasındaki mesafenin üçte ikisidir.

## Formül

```text
Pivot=(Y+D+K)/3; BC=(Y+D)/2; TC=2*Pivot-BC
```

## Parametreler

**Gerekli girdiler:** `high`, `low`, `close`

_Yok._

## Döndürdükleri

| Kolon |
| --- |
| `CPR_PIVOT` |
| `CPR_BC` |
| `CPR_TC` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.cpr(df['high'], df['low'], df['close']).tail(3)
```

```text
            CPR_PIVOT    CPR_BC     CPR_TC
date                                      
2024-10-25  90.649533  90.72185  90.577217
2024-10-26  90.229367  90.29595  90.162783
2024-10-27  89.485600  89.66890  89.302300
```

**Accessor biçimi:** `df.zta.cpr(...)`

## Nasıl okunur

Dar bir CPR, önceki barın kendi aralığının ortasına yakın kapandığı (kararsızlık, genellikle daha büyük bir hareketin öncüsü) anlamına gelir; geniş bir CPR ise bir uca yakın kapandığı (yönlü bir bar, genellikle devamın öncüsü) anlamına gelir.

## Dikkat edilmesi gerekenler

`pivot_points` gibi, seviyeler **önceki** bardan hesaplanır ve mevcut bara uygulanır — günlük CPR seviyeleri için günlük bar, haftalık için haftalık bar verin.

## Kaynak

Formül kaynağı: [https://www.luxalgo.com/library/concept/central-pivot-range/](https://www.luxalgo.com/library/concept/central-pivot-range/)
