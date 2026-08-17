# Fibonacci Geri Çekilmesi

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/fib_retracement.md)

`zeonta.fib_retracement()` — Fibonacci retracement levels drawn from the most recent swing.

## Ne ölçer

Güçlü bir hareketin ardından fiyat nadiren doğrudan devam eder — bir kısmını geri verir. Fibonacci geri çekilmesi, bu geri çekilmenin en sık durduğu hareket kesirlerini işaretler. Bu uygulama swing'i kayan bir pencereden otomatik seçer.

## Formül

```text
Oranlar = 0,236, 0,382, 0,5, 0,618, 0,786 (Fibonacci dizisinden türetilir, 0,5 gelenek olarak dahil edilir); yükseliş trendinden sonra, seviye = Yüksek - (Yüksek - Düşük) x oran; düşüş trendinden sonra, seviye = Düşük + (Yüksek - Düşük) x oran; uzatmalar hedefleri yansıtmak için %100'ün ötesinde aynı oranları kullanır (%127,2, %161,8, %261,8)
```

## Parametreler

**Gerekli girdiler:** `high`, `low`

| Parametre | Varsayılan |
| --- | --- |
| `lookback` | `100` |
| `ratios` | `(0.236, 0.382, 0.5, 0.618, 0.786)` |
| `extensions` | `False` |

## Döndürdükleri

| Kolon |
| --- |
| `FIB_0` |
| `FIB_1` |
| `FIB_0.236` |
| `FIB_0.382` |
| `FIB_0.5` |
| `FIB_0.618` |
| `FIB_0.786` |
| `FIBDIR` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.fib_retracement(df['high'], df['low'], lookback=60)[['FIB_0', 'FIB_0.382', 'FIB_0.618', 'FIB_1', 'FIBDIR']].tail(3)
```

```text
              FIB_0  FIB_0.382  FIB_0.618    FIB_1  FIBDIR
date                                                      
2024-10-25  88.9268  90.835769  92.015131  93.9241    -1.0
2024-10-26  88.9268  90.835769  92.015131  93.9241    -1.0
2024-10-27  88.0724  90.307749  91.688751  93.9241    -1.0
```

**Accessor biçimi:** `df.zta.fib_retracement(...)`

## Nasıl okunur

0,382-0,618 bölgesi, işlem yapılabilir geri çekilmelerin çoğunun bittiği yerdir; 0,786 ise hareketin genellikle başarısız sayılmasından önceki son seviyedir. `FIBDIR` swing'in hangi yöne gittiğini söyler; böylece seviyelerin zirveden aşağı mı yoksa dipten yukarı mı ölçüldüğünü bilirsiniz.

## Dikkat edilmesi gerekenler

Fibonacci seviyeleri fiziksel bir sebepten değil, yeterince çok yatırımcı aynı çizgileri çizdiği için çalışır. Farklı swing seçen iki kişi farklı seviyeler bulur ve ikisi de "haklı" olabilir. Buradaki swing her barda yeniden hesaplandığı için yeni uç noktalar oluştukça seviyeler yeniden çizilir.

## Kaynak

Formül kaynağı: [https://ta.cognicode.org/learn/fibonacci](https://ta.cognicode.org/learn/fibonacci)
