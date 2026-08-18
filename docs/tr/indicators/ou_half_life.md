# Ortalamaya Dönüşün Ornstein-Uhlenbeck Yarı Ömrü

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/ou_half_life.md)

`zeonta.ou_half_life()` — Ornstein-Uhlenbeck half-life: bars until a mean-reverting series closes half its gap.

## Ne ölçer

Ornstein-Uhlenbeck süreci, kantitatif finansta ortalamaya dönen bir seri için standart sürekli-zamanlı modeldir; bunu fiyata uyumlayıp uyumlanan ortalamaya-dönüş hızını bir yarı ömre çevirmek — fiyat ile kendi ima ettiği uzun vadeli seviyesi arasındaki farkın yarısının kaç barda kapanacağı — bir ortalamaya-dönüş stratejisi için *geriye bakış uzunluğu* seçmenin yaygın kullanılan bir yoludur, tek başına bir sinyal okuması değil. Bir serinin genel olarak kalıcı mı yoksa kalıcı-olmayan mı olduğunu soran hurst_exponent'in aksine, bu, zaten ortalamaya döndüğü varsayılan bir seriye daha dar, daha eyleme dönüştürülebilir bir soru sorar: ne kadar hızlı.

## Formül

```text
Yuvarlanan bir pencere üzerinde Close[t]-Close[t-1]'i Close[t-1]'e karşı regresyona sok (OLS); lambda = uyumlanan eğim; OUHL = -ln(2)/lambda (lambda < 0 ise), aksi halde NaN
```

## Parametreler

**Gerekli girdiler:** `close`

| Parametre | Varsayılan |
| --- | --- |
| `window` | `100` |

## Döndürdükleri

| Kolon |
| --- |
| `OUHL_100` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.ou_half_life(df['close']).tail(3)
```

```text
date
2024-10-25    11.424672
2024-10-26    16.224036
2024-10-27    25.045121
Name: OUHL_100, dtype: float64
```

**Accessor biçimi:** `df.zta.ou_half_life(...)`

## Nasıl okunur

Kısa bir yarı ömür (birkaç bar) dönüşün hızlı olduğu anlamına gelir — bir ortalamaya-dönüş girişinin yakında kapanması beklenebilir. Uzun bir yarı ömür, dönüşün yavaş olduğu, hatta güvenilir şekilde gerçekleşip gerçekleşmediğinin bile belirsiz olduğu anlamına gelir; `NaN`, o pencerede uyumlanan `lambda`'nın >= 0 olduğu anlamına gelir — orada ortalamaya dönüş tespit edilmedi, yani ortalamaya-dönüş işleminin tüm önermesi şu anda geçerli değil. Yatırımcılar genellikle yarı ömür değerinin kendisini doğrudan işlem yapmak yerine başka bir indikatör ya da stratejinin geriye-bakış/tutma-süresi parametresi olarak kullanır.

## Dikkat edilmesi gerekenler

Bu uyum, serinin ortalamaya-dönüş davranışının tüm yuvarlanan pencere boyunca kabaca sabit kaldığını varsayar — pencerenin ortasında bir rejim değişikliği (seri ortalamaya dönmeyi durdurur ya da başlar) tahmini, temiz bir ayrım yerine pencerede baskın olan davranışa doğru yanlı hale getirir. Ve `hurst_exponent` gibi, bu da literatürdeki tek yöntem değil, belirli, standart bir tahmin yöntemidir (ayrıklaştırılmış süreç üzerinde OLS).

## Kaynak

Formül kaynağı: [https://en.wikipedia.org/wiki/Ornstein%E2%80%93Uhlenbeck_process](https://en.wikipedia.org/wiki/Ornstein%E2%80%93Uhlenbeck_process)
