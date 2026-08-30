# Niceliksel Niteliksel Tahmin (QQE)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/qqe.md)

`zeonta.qqe()` — A smoothed RSI with an ATR-style trailing band, flipping like a Supertrend on RSI.

## Ne ölçer

[rsi](rsi.md)'yi bir EMA ile yumuşatır, bu yumuşatılmış çizginin kendi bar-başı oynaklığını ölçer (iki kez Wilder-yumuşatılmış) ve yumuşatılmış RSI etrafında bir takip bandı inşa etmek için kullanır — [supertrend](supertrend.md)'in fiyat üzerinde kullandığı aynı tek-yönlü-vinç, kesişimde-dönme inşası, burada RSI'ye uygulanır. QQE'nin arkasında tek bir akademik makale yoktur — bir MetaTrader topluluk indikatörü olarak ortaya çıkmıştır — ama inşası kesindir ve birden fazla bağımsız uygulama arasında aynı şekilde çapraz doğrulanmıştır, bu kütüphanenin tam olarak bu eksiklik yüzünden reddettiği indikatörlerden farklı olarak.

## Formül

```text
RsiMa = EMA(RSI, smooth); DeltaFastAtrRsi = EMA(EMA(|ΔRsiMa|, 2n-1), 2n-1)*factor; takip eden bant, RsiMa üzerine kurulmuş bir Supertrend gibi döner
```

## Parametreler

**Gerekli girdiler:** `close`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `14` |
| `smooth` | `5` |
| `factor` | `4.236` |

## Döndürdükleri

| Kolon |
| --- |
| `QQE_14_5_4.236` |
| `QQEl_14_5_4.236` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.qqe(df['close']).tail(3)
```

```text
            QQE_14_5_4.236  QQEl_14_5_4.236
date                                       
2024-10-25       43.655912        46.597895
2024-10-26       41.498870        46.597895
2024-10-27       38.946936        45.623334
```

**Accessor biçimi:** `df.zta.qqe(...)`

## Nasıl okunur

Takip çizgisinin kendi değeri, fiyat/RSI onun üzerinde kaldığı sürece yükseliş desteği, altında kaldığında ise dirençtir — yumuşatılmış RSI ile takip çizgisi arasındaki kesişimi `supertrend`'in dönüşlerini okuduğunuz gibi okuyun, ya da yumuşatılmış RSI'nin kendi 50 orta çizgisini kesmesini izleyin.

## Dikkat edilmesi gerekenler

Uzun bir ısınma süresine ihtiyaç duyar — çift-yumuşatılmış oynaklık terimi tek başına, bir değer üretmeden önce RSI'nin kendi ısınmasının üzerine kabaca `2*(2*length-1)` bara ihtiyaç duyar.

## Kaynak

Formül kaynağı: [https://www.prorealcode.com/prorealtime-indicators/qqe-indicator-quantitative-qualitative-estimation/](https://www.prorealcode.com/prorealtime-indicators/qqe-indicator-quantitative-qualitative-estimation/)
