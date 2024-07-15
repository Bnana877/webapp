from fastapi import HTTPException

from models import DataModel
import rate


def pred_set(data: DataModel):
    likelihood = [(1.0 if s > 0.0 else 0.0) for s in data.settings]
    saki_flag = False
    for sample in data.history:
        if sample.icon == "":
            continue
        if sample.icon == "先読み":
            likelihood[0] = 0
            for setting in range(6):
                if saki_flag:
                    likelihood[setting] *= 0
                elif sample.cycle > 98:
                    likelihood[setting] *= 0.046
                elif sample.cycle % 55 == 0:
                    likelihood[setting] *= 0.25
                elif sample.cycle % 10 == 0:
                    likelihood[setting] *= 0.046
                elif sample.cycle % 10 == 5:
                    likelihood[setting] *= 0.006
                else:
                    likelihood[setting] *= 0.004
            saki_flag = True
            continue
        else:
            for setting in range(6):
                if saki_flag:
                    likelihood[setting] *= 1.0 - 0
                elif sample.cycle > 98:
                    likelihood[setting] *= 1.0 - 0.046
                elif sample.cycle % 55 == 0:
                    likelihood[setting] *= 1.0 - 0.25
                elif sample.cycle % 10 == 0:
                    likelihood[setting] *= 1.0 - 0.046
                elif sample.cycle % 10 == 5:
                    likelihood[setting] *= 1.0 - 0.006
                else:
                    likelihood[setting] *= 1.0 - 0.04

        for setting in range(6):
            if saki_flag:
                likelihood[setting] *= rate.rate_saki[f"{setting + 1}"][sample.icon]
            elif sample.cycle > 98:
                likelihood[setting] *= rate.rate_99[f"{setting + 1}"][sample.icon]
            elif sample.cycle % 55 == 0:
                likelihood[setting] *= rate.rate_55[f"{setting + 1}"][sample.icon]
            elif sample.cycle % 5 == 0:
                likelihood[setting] *= rate.rate_05[f"{setting + 1}"][sample.icon]
            else:
                likelihood[setting] *= rate.rate_def[f"{setting + 1}"][sample.icon]
        saki_flag = False

    try:
        bayes = [s / sum(sorted(data.settings)) for s in data.settings]
        bayes_sum = sum(sorted([bayes[_] * likelihood[_] for _ in range(6)]))
        result = {
            "likelihood": [s / sum(sorted(likelihood)) for s in likelihood],
            "bayes": [(bayes[_] * likelihood[_]) / bayes_sum for _ in range(6)]
        }
    except ZeroDivisionError:
        raise HTTPException(status_code=400, detail="存在しない組み合わせです.")
    return result
