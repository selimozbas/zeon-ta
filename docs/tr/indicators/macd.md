# MACD (Hareketli Ortalama Yakınsama Iraksama)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/macd.md)

`zeonta.macd()` — Difference between two EMAs, with a signal line and histogram.

## Ne ölçer

MACD, hızlı ve yavaş EMA arasındaki mesafeyi kendi başına bir seriye dönüştürür. Bu mesafe trend hızlandığında büyür, yorulduğunda küçülür; bu da MACD'yi tamamen trend araçlarından kurulmuş bir momentum okuması yapar.

## Formül

```text
MACD Çizgisi = EMA(12) - EMA(26); Sinyal Çizgisi = MACD Çizgisi'nin EMA(9)'u; Histogram = MACD Çizgisi - Sinyal Çizgisi
```

## Parametreler

**Gerekli girdiler:** `close`

| Parametre | Varsayılan |
| --- | --- |
| `fast` | `12` |
| `slow` | `26` |
| `signal` | `9` |

## Döndürdükleri

| Kolon |
| --- |
| `MACD_12_26_9` |
| `MACDs_12_26_9` |
| `MACDh_12_26_9` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.macd(df['close']).tail(3)
```

```text
            MACD_12_26_9  MACDs_12_26_9  MACDh_12_26_9
date                                                  
2024-10-25     -0.381243      -0.343159      -0.038084
2024-10-26     -0.462624      -0.367052      -0.095572
2024-10-27     -0.571910      -0.408024      -0.163887
```

**Accessor biçimi:** `df.zta.macd(...)`

## Nasıl okunur

Çoğu kişinin asıl işlem yaptığı kısım histogramdır: MACD çizgisi sinyalini kestiği anda sıfırı keser ve yüksekliği farkın ne kadar hızlı değiştiğini gösterir. MACD'nin sıfırın üstünde olması, hızlı EMA'nın yavaşın üstünde olduğu — yani o tanıma göre bir yükseliş trendi olduğu — anlamına gelir.

## Dikkat edilmesi gerekenler

MACD sınırsızdır ve değerleri fiyatla birlikte ölçeklenir; dolayısıyla 3 değeri 20 dolarlık bir hissede ve 2.000 dolarlık bir hissede tamamen farklı şey ifade eder — ham MACD'yi asla semboller arasında karşılaştırmayın. Ayrıca iki kez yumuşatılmış bir trend aracı olarak yatay bantta ciddi biçimde testere hareketi yapar.

## Kaynak

Formül kaynağı: [https://ta.cognicode.org/learn/macd](https://ta.cognicode.org/learn/macd)
