# ADX Derecelendirmesi (ADXR)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/adxr.md)

`zeonta.adxr()` — ADX averaged with its own value from length-1 bars ago, smoothing its tops/bottoms.

## Ne ölçer

[adx](adx.md)'in yumuşatılmış bir uzantısı: bugünün ADX'i, kendi ``length - 1`` bar önceki değeriyle ortalanır. `trima`'nın çift-SMA geçişinin fiyata uyguladığı aynı fikir, burada ADX'e uygulanır — trend-gücü okumasındaki sahte tepe ve dipler için biraz daha fazla gecikme ile takas edilir.

## Formül

```text
ADXR = (ADX + ADX[length - 1 bar önce]) / 2
```

## Parametreler

**Gerekli girdiler:** `high`, `low`, `close`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `14` |

## Döndürdükleri

| Kolon |
| --- |
| `ADXR_14` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.adxr(df['high'], df['low'], df['close']).tail(3)
```

```text
date
2024-10-25    16.628347
2024-10-26    16.505838
2024-10-27    17.121435
Name: ADXR_14, dtype: float64
```

**Accessor biçimi:** `df.zta.adxr(...)`

## Nasıl okunur

Tam olarak `adx` gibi okunur — yükselen bir ADXR, trendin (hangi yönde olursa olsun) güçlendiği anlamına gelir. `adx`'in kendisinden daha pürüzsüzdür, bu yüzden ADXR'nin kendi yönündeki bir değişim, trend gücünün zirve yaptığının ya da dip yaptığının daha istikrarlı bir sinyalidir.

## Dikkat edilmesi gerekenler

Bir değer üretmeden önce yaklaşık ``3 * length`` bara ihtiyaç duyar — `adx`'in kendi ``2 * length``-barlık ısınması, artı ortalamasını aldığı gecikmeli kopya için ``length - 1`` bar daha.

## Kaynak

Formül kaynağı: [https://www.fmlabs.com/reference/ADXR.htm](https://www.fmlabs.com/reference/ADXR.htm)
