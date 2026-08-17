# Destek ve Direnç

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/support_resistance.md)

`zeonta.support_resistance()` — Confirmed swing pivots and the most recent support/resistance they mark.

## Ne ölçer

Destek ve direnç, göz kararı çizilen çizgiler değildir — piyasanın fiilen döndüğü fiyatlardır. Bu fonksiyon o dönüş noktalarını swing pivotları olarak mekanik biçimde bulur, ardından en son teyit edilmiş olanı kullanılabilir bir seviye olarak ileri taşır.

## Formül

```text
Pivot Yüksek(leftBars, rightBars), i barında: Yüksek[i] > Yüksek[i-leftBars..i-1] ve Yüksek[i] > Yüksek[i+1..i+rightBars] (yerel tepe). Pivot Düşük bunun aynadaki karşılığıdır. Birden fazla pivotun kümelendiği fiyat, destek/direnç seviyesi olur.
```

## Parametreler

**Gerekli girdiler:** `high`, `low`

| Parametre | Varsayılan |
| --- | --- |
| `left` | `10` |
| `right` | `10` |

## Döndürdükleri

| Kolon |
| --- |
| `PIVOTHIGH_10_10` |
| `PIVOTLOW_10_10` |
| `RES_10_10` |
| `SUP_10_10` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.support_resistance(df['high'], df['low'], left=5, right=5)[['RES_5_5', 'SUP_5_5']].tail(3)
```

```text
            RES_5_5  SUP_5_5
date                        
2024-10-25  92.9721  89.7116
2024-10-26  92.9721  89.7116
2024-10-27  92.9721  89.7116
```

```python
zeonta.sr_levels(df['high'], df['low'], left=5, right=5, max_levels=3)
```

```text
       level  touches     kind
0  93.029363       16     both
1  95.336044        9     both
2  90.813267        3  support
```

**Accessor biçimi:** `df.zta.support_resistance(...)`

## Nasıl okunur

`PIVOTHIGH` / `PIVOTLOW` swing'in fiilen oluştuğu yeri işaretler. `RES` / `SUP` en son teyit edilmiş seviyeyi tutar; işlem yaparken kullanılacak kolonlar bunlardır. Kümelenmiş seviyeleri kaç kez test edildiklerine göre sıralı istiyorsanız `sr_levels()` kullanın.

## Dikkat edilmesi gerekenler

Bir pivot, sağında `right` bar daha oluşana kadar bilinemez; bu yüzden `PIVOTHIGH` / `PIVOTLOW` kolonları geleceğe bakma (look-ahead) bilgisi içerir — pivotu öğrendiğiniz bara değil, oluştuğu bara koyarlar. Geriye dönük testlerde `right` bar gecikmeli olan `RES` / `SUP` kolonlarını kullanın.
