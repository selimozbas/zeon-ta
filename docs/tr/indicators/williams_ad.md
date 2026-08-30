# Williams Birikim/Dağıtım (WAD)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/williams_ad.md)

`zeonta.williams_ad()` — Running total gated by whether today extended a rising or falling close.

## Ne ölçer

Larry Williams'ın [adl](adl.md)'nin öncülü: ADL bir barı, kapanışın *o barın kendi* aralığının neresinde oturduğuna göre ağırlıklandırırken, WAD her barı bunun yerine *önceki* kapanışa göre sabitler — yukarı boşluk veren bir bar, yalnızca dünün kapanışının üstündeki hareket için kredi alır, kendi tam aralığı için değil. ADL/OBV ile aynı kategoride yaşamasına rağmen hacim terimi yoktur.

## Formül

```text
TRH = max(Kapanış[-1], Yüksek); TRL = min(Kapanış[-1], Düşük); WAD += (Kapanış-TRL) Kapanış yükseldiyse, (Kapanış-TRH) düştüyse, aksi halde değişmez
```

## Parametreler

**Gerekli girdiler:** `high`, `low`, `close`

_Yok._

## Döndürdükleri

| Kolon |
| --- |
| `WAD` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.williams_ad(df['high'], df['low'], df['close']).tail(3)
```

```text
date
2024-10-25   -17.4391
2024-10-26   -18.5619
2024-10-27   -19.7192
Name: WAD, dtype: float64
```

**Accessor biçimi:** `df.zta.williams_ad(...)`

## Nasıl okunur

`adl`/`obv` ile aynı şekilde okunur — yükselen fiyatla birlikte yükselen bir çizgi trendi doğrular; fiyatla birlikte yeni bir zirve yapamama bir uyumsuzluk uyarısıdır.

## Dikkat edilmesi gerekenler

`adl`/`obv`/`pvt` gibi keyfi bir başlangıç seviyesine sahip süregelen bir toplam — yalnızca eğimi ve fiyattan sapması anlam taşır.

## Kaynak

Formül kaynağı: [https://tulipindicators.org/wad](https://tulipindicators.org/wad)
