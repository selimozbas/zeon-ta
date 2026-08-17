# Göreceli Güç Endeksi (RSI)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/rsi.md)

`zeonta.rsi()` — Wilder's momentum oscillator bounded between 0 and 100.

## Ne ölçer

RSI dar bir soru sorar: son n barda toplam hareketin ne kadarı yukarı yönlüydü? Cevap 0-100 ölçeğine sıkıştırılır; bu da momentumu semboller ve zaman dilimleri arasında karşılaştırılabilir kılar.

## Formül

```text
RSI = 100 - 100 / (1 + RS), RS = OrtalamaKazanç(14, Wilder) / OrtalamaKayıp(14, Wilder)
```

## Parametreler

**Gerekli girdiler:** `close`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `14` |

## Döndürdükleri

| Kolon |
| --- |
| `RSI_14` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.rsi(df['close'], length=14).tail(3)
```

```text
date
2024-10-25    43.273375
2024-10-26    37.184787
2024-10-27    33.843069
Name: RSI_14, dtype: float64
```

**Accessor biçimi:** `df.zta.rsi(...)`

## Nasıl okunur

70'in üstü geleneksel olarak "aşırı alım", 30'un altı "aşırı satım" sayılır; ancak daha kalıcı olan okuma 50 çizgisidir: geri çekilmeler boyunca 50'nin üstünde tutunan RSI, sağlıklı bir trendi gösterir. RSI ile fiyat arasındaki uyumsuzluk diğer klasik kullanımdır — bkz. [divergence](divergence.md).

## Dikkat edilmesi gerekenler

"Aşırı alım", "düşmek üzere" demek değildir. Güçlü bir trendde RSI haftalarca 70'in üstünde kalabilir ve her böyle okumada açığa satmak, bu göstergeyle para kaybetmenin en güvenilir yollarından biridir. 70/30'u bir talimat değil, momentumun tarifi olarak görün.
