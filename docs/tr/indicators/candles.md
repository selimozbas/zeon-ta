# Mum Anatomisi ve Formasyonlar

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/candles.md)

`zeonta.candles()` — Candle body/wick geometry plus doji, engulfing and hammer detection.

## Ne ölçer

Bir mum dört sayıyı tek bir şekle sıkıştırır: işlemin nerede açılıp kapandığı (gövde) ve arada nereye kadar saptığı (fitiller). Bu fonksiyon o geometriyi düz kolonlar hâlinde döndürür; ayrıca en sık karşılaşılan üç formasyonu işaretler: doji, yutan mum çifti ve çekiç/kayan yıldız.

## Formül

```text
Gövde = |Kapanış - Açılış|; Kapanış > Açılış ise boğa mumu, Kapanış < Açılış ise ayı mumu; Üst fitil = En Yüksek - max(Açılış, Kapanış); Alt fitil = min(Açılış, Kapanış) - En Düşük.
```

## Parametreler

**Gerekli girdiler:** `open`, `high`, `low`, `close`

| Parametre | Varsayılan |
| --- | --- |
| `doji_threshold` | `0.1` |
| `hammer_ratio` | `2.0` |

## Döndürdükleri

| Kolon |
| --- |
| `CDLBODY` |
| `CDLUPPER` |
| `CDLLOWER` |
| `CDLRANGE` |
| `CDLDIR` |
| `CDLDOJI` |
| `CDLENG` |
| `CDLHAM` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.candles(df['open'], df['high'], df['low'], df['close'])[['CDLBODY', 'CDLDIR', 'CDLDOJI', 'CDLENG']].tail(3)
```

```text
            CDLBODY  CDLDIR  CDLDOJI  CDLENG
date                                        
2024-10-25   0.3995    -1.0      0.0     0.0
2024-10-26   1.0998    -1.0      0.0     0.0
2024-10-27   0.7475    -1.0      0.0     0.0
```

**Accessor biçimi:** `df.zta.candles(...)`

## Nasıl okunur

Uzun gövde, seansın tamamına bir tarafın hâkim olduğunu; uzun fitil ise bir seviyenin test edilip reddedildiğini gösterir. `CDLDIR` yönü verir, `CDLDOJI` kararsızlığı işaretler, `CDLENG` dönüş çiftini (+1 boğa, -1 ayı), `CDLHAM` ise reddetme mumunu (+1 çekiç, -1 kayan yıldız) bildirir.

## Dikkat edilmesi gerekenler

Formasyon bir ya da iki barın tarifidir, sinyal değildir. Yatay bir bandın ortasındaki çekiç hiçbir şey ifade etmez; aynı çekiç daha önce iki kez test edilmiş bir seviyede ise anlam kazanır. Formasyonu daima konumla birlikte okuyun.

## Kaynak

Formül kaynağı: [https://ta.cognicode.org/learn/candlesticks](https://ta.cognicode.org/learn/candlesticks)
