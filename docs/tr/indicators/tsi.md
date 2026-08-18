# Gerçek Güç Endeksi (TSI)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/tsi.md)

`zeonta.tsi()` — Double-smoothed momentum, bounded and steadier than a single-pass oscillator.

## Ne ölçer

William Blau'nun çift yumuşatması, herhangi bir oran alınmadan önce ham fiyat değişiminin kendisi üzerinde çalışır — bu, önce kazanç/kayıpları ayrı ortalamalara dönüştürüp ancak sonra bölen `rsi`'nin tam tersi bir sıradır. TSI'nin önce-çift-EMA yaklaşımı, kısa vadeli gürültüyü filtrelerken altta yatan trendi yakından takip etmeyi hedefler.

## Formül

```text
PC = Kapanış - Kapanış[1 bar önce]; ÇiftYumuşatılmışPC = EMA(EMA(PC, uzun), kısa); ÇiftYumuşatılmışMutlakPC = EMA(EMA(|PC|, uzun), kısa); TSI = 100 x ÇiftYumuşatılmışPC / ÇiftYumuşatılmışMutlakPC; Sinyal = EMA(TSI, sinyal)
```

## Parametreler

**Gerekli girdiler:** `close`

| Parametre | Varsayılan |
| --- | --- |
| `long` | `25` |
| `short` | `13` |
| `signal` | `7` |

## Döndürdükleri

| Kolon |
| --- |
| `TSI_25_13_7` |
| `TSIs_25_13_7` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.tsi(df['close']).tail(3)
```

```text
            TSI_25_13_7  TSIs_25_13_7
date                                 
2024-10-25   -12.260304    -11.761409
2024-10-26   -14.523263    -12.451873
2024-10-27   -17.545947    -13.725391
```

**Accessor biçimi:** `df.zta.tsi(...)`

## Nasıl okunur

Aşırı alım/aşırı satım okumaları, orta çizgi kesişimleri, sinyal çizgisi kesişimleri ve uyumsuzluklar — hepsi geçerlidir, `rsi` ve `macd`'nin birleşimi gibi bir kelime dağarcığı. TSI, tepe ve diplerinin genellikle fiyatın kendi tepe ve dipleriyle yakından örtüşmesi bakımından biraz sıra dışıdır — güçlü, sürdürülen bir hareket sırasında düzleşen osilatörlerin aksine.

## Dikkat edilmesi gerekenler

Ne StockCharts ne de Fidelity'nin kılavuzu tek bir kanonik varsayılan sinyal-çizgisi periyoduna bağlanır — bu uygulama (25, 13) çekirdek yumuşatma çiftiyle birlikte, bağımsız kaynaklar arasında en sık tekrarlanan değer olan 7'yi kullanır, ama TSI(25,13,13) ve TSI(40,20,10) da yaygın olarak kullanılır.

## Kaynak

Formül kaynağı: [https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/true-strength-index](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/true-strength-index)
