# EMA Şeridi

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/ema_ribbon.md)

`zeonta.ema_ribbon()` — A fan of EMAs of increasing length; spacing shows trend strength.

## Ne ölçer

Tek bir EMA size trendi söyler; altı tanesi ne kadar uzlaşma olduğunu söyler. Yelpazenin tamamı aynı yönü gösterip açıldığında, şeritteki her zaman dilimi hemfikirdir. Birbirine düğümlendiğinde ise hiçbiri değildir.

## Formül

```text
EMA Şeridi = birlikte çizilen, artan uzunlukta 6 EMA, örn. EMA(20), EMA(30), EMA(40), EMA(50), EMA(60), EMA(70) (ya da Fibonacci benzeri: 8, 13, 21, 34, 55, 89). Her EMA(n) = Kapanış x k + önceki EMA(n) x (1 - k), k = 2/(n+1).
```

## Parametreler

**Gerekli girdiler:** `close`

| Parametre | Varsayılan |
| --- | --- |
| `lengths` | `(20, 30, 40, 50, 60, 70)` |

## Döndürdükleri

| Kolon |
| --- |
| `EMA_20` |
| `EMA_30` |
| `EMA_40` |
| `EMA_50` |
| `EMA_60` |
| `EMA_70` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.ema_ribbon(df['close'], lengths=(8, 13, 21, 34, 55, 89)).tail(2)
```

```text
                EMA_8     EMA_13     EMA_21     EMA_34     EMA_55     EMA_89
date                                                                        
2024-10-26  90.083492  90.323343  90.599422  90.956204  91.463247  92.183236
2024-10-27  89.727649  90.060322  90.406948  90.814833  91.356781  92.100991
```

**Accessor biçimi:** `df.zta.ema_ribbon(...)`

## Nasıl okunur

Genişçe açılmış ve doğru sıralanmış (yükseliş trendinde en kısası üstte) olması güçlü, yerleşmiş bir trend demektir. Sıkışmış ve iç içe geçmiş olması trendin durakladığını gösterir — çoğu zaman her iki yönde de belirleyici bir hareketin hemen öncesinde.

## Dikkat edilmesi gerekenler

Şerit, altı bağımsız görüş değil, altı gecikmeli göstergedir — hepsi aynı kapanışlardan gelir, dolayısıyla "uzlaşmaları" göründüğünden çok daha zayıf bir kanıttır. Sinyal üreticisinden çok bir görselleştirme yardımcısıdır.

## Kaynak

Formül kaynağı: [https://ta.cognicode.org/learn/ema-ribbon](https://ta.cognicode.org/learn/ema-ribbon)
