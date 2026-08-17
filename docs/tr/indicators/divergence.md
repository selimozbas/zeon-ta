# Uyumsuzluklar

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/divergence.md)

`zeonta.divergence()` — Regular and hidden divergences between price swings and an oscillator.

## Ne ölçer

Fiyat yeni bir uç nokta yaparken osilatör yapmıyorsa, bu hareket bir öncekinden daha az güçle yapılıyordur. Bu uyuşmazlık — uyumsuzluk — teknik analizdeki gerçekten ileriye dönük az sayıdaki şeyden biridir.

## Formül

```text
Normal Ayı = fiyat Daha Yüksek Tepe + osilatör Daha Düşük Tepe; Normal Boğa = fiyat Daha Düşük Dip + osilatör Daha Yüksek Dip; Gizli Ayı = fiyat Daha Düşük Tepe + osilatör Daha Yüksek Tepe; Gizli Boğa = fiyat Daha Yüksek Dip + osilatör Daha Düşük Dip
```

## Parametreler

**Gerekli girdiler:** `high`, `low`, `close`

| Parametre | Varsayılan |
| --- | --- |
| `oscillator` | `None` |
| `osc_length` | `14` |
| `left` | `5` |
| `right` | `5` |

## Döndürdükleri

| Kolon |
| --- |
| `DIVREGBULL_5_5` |
| `DIVREGBEAR_5_5` |
| `DIVHIDBULL_5_5` |
| `DIVHIDBEAR_5_5` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.divergence(df['high'], df['low'], df['close'], left=5, right=5).sum()
```

```text
DIVREGBULL_5_5    2.0
DIVREGBEAR_5_5    3.0
DIVHIDBULL_5_5    0.0
DIVHIDBEAR_5_5    4.0
dtype: float64
```

**Accessor biçimi:** `df.zta.divergence(...)`

## Nasıl okunur

Normal uyumsuzluk trendin yorulduğunu ve dönüşün yaklaştığını savunur. Gizli uyumsuzluk ise tam tersini savunur: trend içindeki bir geri çekilme bitiyordur ve trend yeniden başlamak üzeredir. Varsayılan osilatör RSI(14)'tür; `oscillator` ile herhangi bir seri geçebilirsiniz.

## Dikkat edilmesi gerekenler

Uyumsuzluk bir uyarıdır, sinyal değil — güçlü bir trendde osilatör, fiyat yoluna devam ederken üç dört kez uyumsuzluk verebilir ve her biri geriye bakınca ikna edici görünür. Fiyat teyidini bekleyin. Ayrıca işaretler pivot barına düşer ve bu bar ancak `right` bar sonra bilinebilir: geriye dönük testten önce çıktıyı kaydırın.
