# Sıkışma (TTM Squeeze)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/squeeze.md)

`zeonta.squeeze()` — Detects Bollinger Bands compressed inside Keltner Channels, plus a momentum read.

## Ne ölçer

Farklı hızlarda tepki veren iki oynaklık ölçüsünün birbiriyle karşılaştırılması. Hızlı olan (Bollinger), yavaş olanın (Keltner) içine büzüldüğünde oynaklık olağandışı ölçüde sıkışmıştır — ve sıkışmış oynaklık genişleme eğilimindedir.

## Formül

```text
Sıkışma AÇIK: BB Üst < KC Üst VE BB Alt > KC Alt (Bollinger Bantları tamamen Keltner Kanalının içine sıkışmış); Momentum = DoğrusalRegresyon(Kapanış - Ortalama(EnYüksekZirve(n), EnDüşükDip(n), HO(Kapanış,n)), n)
```

## Parametreler

**Gerekli girdiler:** `high`, `low`, `close`

| Parametre | Varsayılan |
| --- | --- |
| `bb_length` | `20` |
| `bb_std` | `2.0` |
| `kc_length` | `20` |
| `kc_multiplier` | `1.5` |

## Döndürdükleri

| Kolon |
| --- |
| `SQZ_ON_20_2.0_20_1.5` |
| `SQZ_OFF_20_2.0_20_1.5` |
| `SQZ_MOM_20_2.0_20_1.5` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.squeeze(df['high'], df['low'], df['close']).tail(3)
```

```text
            SQZ_ON_20_2.0_20_1.5  SQZ_OFF_20_2.0_20_1.5  SQZ_MOM_20_2.0_20_1.5
date                                                                          
2024-10-25                   1.0                    0.0              -0.410355
2024-10-26                   1.0                    0.0              -0.675908
2024-10-27                   0.0                    1.0              -0.975041
```

**Accessor biçimi:** `df.zta.squeeze(...)`

## Nasıl okunur

`SQZ_ON` sıkışmayı işaretler; yatırımcıların asıl işlem yaptığı bar ise `SQZ_OFF`'un ilk açıldığı bar, yani serbest kalma barıdır. Yönü momentum histogramı verir: serbest kalma anında sıfırın üstünde yükselen barlar yukarıyı, sıfırın altında düşen barlar aşağıyı işaret eder.

## Dikkat edilmesi gerekenler

Sıkışma bir hareketin muhtemel olduğunu söyler, hangi yöne olacağını asla söylemez — momentum okuması olmadan işlem yapmak yazı tura atmaktır. Ayrıca `kc_multiplier`'ı büyütmek Keltner bantlarını dışarı iter ve dolayısıyla sıkışmaları **daha** sık hâle getirir, daha seyrek değil; bu kütüphane, tersini söyleyen TA 101 sınav cevabını değil formülü esas alır. Momentum orta çizgisi, dersin ifadesinin çağrıştırdığı eşit üçlü ortalamayı değil, yayımlanmış TTM tanımındaki *iç içe* ortalamayı kullanır — `avg(avg(hh, ll), sma)`, yani aralık orta noktası ve SMA yarımşar ağırlıkla. Bu nedenle değerler, ifadeyi birebir izleyen bir uygulamadan farklı çıkar.

## Kaynak

Formül kaynağı: [https://ta.cognicode.org/learn/squeeze](https://ta.cognicode.org/learn/squeeze)
