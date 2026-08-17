# SuperTrend

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/supertrend.md)

`zeonta.supertrend()` — ATR-based trailing line that flips between support and resistance.

## Ne ölçer

Yükseliş trendinde fiyatın altında, düşüş trendinde üstünde duran tek bir çizgi. Bir hareketli ortalamanın aksine fiyatı gecikmeli bir eğriye yumuşatmaz — oynaklığa göre ayarlanmış bir bant kurar ve fiyat bir dönüşe zorlayana kadar trendin bu bandın bir tarafına yaslanmasına izin verir.

## Formül

```text
Temel Üst Bant = hl2 + çarpan x ATR(periyot); Temel Alt Bant = hl2 - çarpan x ATR(periyot); Nihai Üst Bant yalnızca aşağı takip eder, Nihai Alt Bant yalnızca yukarı takip eder; SuperTrend = fiyat üzerinde kapanırken (yükseliş) Nihai Alt Bant, fiyat altında kapanırken (düşüş) Nihai Üst Bant; kapanış karşı banda geçtiğinde dönüş gerçekleşir
```

## Parametreler

**Gerekli girdiler:** `high`, `low`, `close`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `10` |
| `multiplier` | `3.0` |

## Döndürdükleri

| Kolon |
| --- |
| `SUPERT_10_3.0` |
| `SUPERTd_10_3.0` |
| `SUPERTl_10_3.0` |
| `SUPERTs_10_3.0` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.supertrend(df['high'], df['low'], df['close'], length=10, multiplier=3)[['SUPERT_10_3.0', 'SUPERTd_10_3.0']].tail(3)
```

```text
            SUPERT_10_3.0  SUPERTd_10_3.0
date                                     
2024-10-25      92.539619            -1.0
2024-10-26      92.539619            -1.0
2024-10-27      92.539619            -1.0
```

**Accessor biçimi:** `df.zta.supertrend(...)`

## Nasıl okunur

`SUPERTd` rejimdir: `1.0` uzun yönlü, `-1.0` kısa yönlü. Tek yönlü kilit mekanizması, çizginin yalnızca trendin lehine hareket etmesini sağlar; bu da onu doğal bir takip eden stop hâline getirir. `SUPERTl` ve `SUPERTs`, iki renkte çizmeye hazır şekilde her rejime maskelenmiş çizgidir.

## Dikkat edilmesi gerekenler

SuperTrend'in trend gücü hakkında bir görüşü yoktur — güçlü bir harekette de cılız bir harekette de aynı şekilde döner. Yatay bantta tekrar tekrar döner ve bunu mekanik bir dur-ve-ters-dön sistemi olarak işleme sokmak arka arkaya küçük zararlar üretir. [adx](adx.md) gibi bir güç filtresiyle birlikte kullanın.

## Kaynak

Formül kaynağı: [https://ta.cognicode.org/learn/supertrend](https://ta.cognicode.org/learn/supertrend)
