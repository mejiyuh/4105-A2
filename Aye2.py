import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

pd.set_option('future.no_silent_downcasting', True)

def normalizeCol(column, featureRange=(1, 5)):
    column = np.array(column)
    minVal = column.min()
    maxVal = column.max()

    #scale  column values to specified featureRange
    scaled_column = (column - minVal) * (featureRange[1] - featureRange[0]) / (
        maxVal - minVal
    ) + featureRange[0]

    return scaled_column

def standardizeCol(column):
    column = np.array(column)
    mean = np.mean(column)
    std = np.std(column)

    column = (column - mean) / std

    return column

def costFunction(X, y, theta, lambda_reg=None):
    predictions = np.dot(X, theta)
    error = predictions - y
    cost = np.sum(error ** 2) / (2 * len(y))

    if lambda_reg is not None:
        # Add regularization term only if lambda_reg is provided
        cost_reg = lambda_reg * np.sum(np.abs(theta))
        cost += cost_reg
        print(f"Regularization cost: {cost_reg}")

    print(f"Cost: {cost}")

    return cost

def multipleDescent(
    X,
    y,
    numFeatures,
    max_iterations=1000,
    learningRate=0.01,
    tolerance=1e-5,
    lambda_reg=None,
    paramPenalty=False,
    verbose=True,
):
    # Convert X to numpy array if it's a pandas Series or DataFrame
    if isinstance(X, pd.Series) or isinstance(X, pd.DataFrame):
        X = X.values

    # Check for NaN or infinity values in X
    if np.isnan(X).any() or np.isinf(X).any():
        raise ValueError("Input data contains NaN or infinity values")

    theta = np.zeros(numFeatures)
    previous_cost = float("-inf")
    costs = []

    lambda_reg = lambda_reg if paramPenalty else None

    for it in range(max_iterations):
        gradient = np.dot(X.T, (np.dot(X, theta) - y)) / len(y)
        if paramPenalty:
            # Add regularization term to the gradient if paramPenalty is True
            gradient += lambda_reg * np.sign(theta)

        theta -= learningRate * gradient

        current_cost = costFunction(X, y, theta, lambda_reg)

        costs.append(current_cost)

        if verbose:
            print(f"Iteration {it}: Cost = {current_cost}, Theta = {theta}")

        if np.isnan(current_cost) or np.isinf(current_cost):
            print("Cost function produced NaN or infinity value.")
            break

        if abs(previous_cost - current_cost) < tolerance:
            break

        previous_cost = current_cost

    plt.plot(np.arange(0, it + 1), costs)
    plt.title(f"Cost over {it} epochs")
    plt.xlabel("Epochs")
    plt.ylabel("mse")
    plt.show()

    print(costs[-1])

    return theta




def readCSV(filepath: str, normalize=False, standardize=False):
    dtypes = {
        "price": int,
        "area": int,
        "bedrooms": int,
        "bathrooms": int,
        "stories": int,
        "mainroad": str,
        "guestroom": str,
        "basement": str,
        "hotwaterheating": str,
        "airconditioning": str,
        "parking": int,
        "prefarea": str,
        "furnishingstatus": str,
    }

    df = pd.read_csv(filepath, dtype=dtypes)
    df.columns = [col.strip() for col in df.columns]  # remove extra whitespace

    # Ensure correct inference of data types
    df = df.infer_objects(copy=False)


    # data sanitization - convert yes and no to 1 and 0
    binary_columns = [
        "mainroad",
        "guestroom",
        "basement",
        "hotwaterheating",
        "airconditioning",
        "prefarea",
    ]
    df[binary_columns] = df[binary_columns].replace({"yes": 1, "no": 0})
    df.infer_objects(copy=False)
    


    # convert furnishedstatus to decimal values between 0-1
    furnishing_mapping = {"unfurnished": 0, "semi-furnished": 0.5, "furnished": 1}
    df["furnishingstatus"] = df["furnishingstatus"].map(furnishing_mapping)
    df = df.infer_objects(copy=False)

    normalize_columns = ["stories", "price", "area", "bedrooms", "bathrooms", "parking"]

    for col in normalize_columns:
        if normalize:
            df[col] = normalizeCol(df[col])
        if standardize:
            df[col] = standardizeCol(df[col])

    # assign inputs and output
    X = df[
        [
            "area",
            "bedrooms",
            "bathrooms",
            "stories",
            "mainroad",
            "guestroom",
            "basement",
            "hotwaterheating",
            "airconditioning",
            "parking",
            "prefarea",
            "furnishingstatus",
        ]
    ]
    y = df["price"]

    # split df into training and validation
    totalRows = len(df)
    trainSize = int(0.8 * totalRows)

    return (X.iloc[:trainSize], y.iloc[:trainSize]), (
        X.iloc[trainSize:],
        y.iloc[trainSize:],
    )

def validateData(Xvalid, yvalid, theta):
    yTrue = []
    for row in Xvalid.values:
        yTrue.append(sum(np.multiply(row, theta)))

    return ((yTrue - yvalid) ** 2).mean()

def plotFeatures(featureNames, theta):
    plt.bar(featureNames, theta)
    plt.xlabel("Features")
    plt.ylabel("Coefficients (Weights)")
    plt.title("Feature Importance")
    plt.show()


def main():
    (xtrain, ytrain), (xvalid, yvalid) = readCSV("./Housing.csv")  # unprocessed
    (nxtrain, nytrain), (nxvalid, nyvalid) = readCSV("./Housing.csv", normalize=True)  # normalized
    (sxtrain, sytrain), (sxvalid, syvalid) = readCSV("./Housing.csv", standardize=True)  # standardized

    # training without normalization/standardization
    print("Raw data training (subset)")
    features = ["area", "bedrooms", "bathrooms", "stories", "parking"]
    theta = multipleDescent(
        xtrain[features],
        ytrain,
        xtrain[features].shape[1],
        learningRate=0.01,
        paramPenalty=False,
    )

    plotFeatures(features, theta)

    print("Raw data training (all)")
    features = [
        "sq.ft",
        "beds",
        "baths",
        "story",
        "road",
        "guest",
        "base",
        "heat",
        "aircon",
        "park",
        "pref",
        "furn",
    ]
    theta = multipleDescent(
        xtrain, ytrain, xtrain.shape[1], learningRate=0.01, paramPenalty=False
    )

    plotFeatures(features, theta)

    # train with normalization (subset)
    print("normalized subset")
    features = ["area", "bedrooms", "bathrooms", "stories", "parking"]
    theta = multipleDescent(
        nxtrain[features],
        nytrain,
        nxtrain[features].shape[1],
        learningRate=0.02,
        paramPenalty=False,
    )

    plotFeatures(features, theta)

    # train with standardization (subset)
    print("standardized subset")
    theta = multipleDescent(
        sxtrain[features],
        sytrain,
        sxtrain[features].shape[1],
        learningRate=0.01,
        paramPenalty=False,
    )

    plotFeatures(features, theta)

    # train with normalization (all)
    print("normalized (all columns)")
    features = [
        "sq.ft",
        "beds",
        "baths",
        "story",
        "road",
        "guest",
        "base",
        "heat",
        "aircon",
        "park",
        "pref",
        "furn",
    ]
    theta = multipleDescent(
        nxtrain, nytrain, nxtrain.shape[1], learningRate=0.01, paramPenalty=False
    )

    plotFeatures(features, theta)
    # train with standardization (all)
    print("standardized (all columns)")
    theta = multipleDescent(
        sxtrain, sytrain, sxtrain.shape[1], learningRate=0.01, paramPenalty=False
    )

    plotFeatures(features, theta)
    # train with parameter penalty (normalization)

    print("Training with a subset of variables (with parameter penalty)")
    features = ["area", "bedrooms", "bathrooms", "stories", "parking"]
    theta = multipleDescent(
        nxtrain[features],
        nytrain,
        nxtrain[features].shape[1],
        learningRate=0.05,
        paramPenalty=True,
        lambda_reg=0.01,
        tolerance=1e-5,
    )

    plotFeatures(features, theta)

    # train with parameter penalty (standardization)

    print("Training with all variables (with parameter penalty)")
    theta = multipleDescent(
        sxtrain,
        sytrain,
        sxtrain.shape[1],
        learningRate=0.01,
        paramPenalty=True,
        lambda_reg=0.2,
        tolerance=1e-5,
    )
    features = [
        "sq.ft",
        "beds",
        "baths",
        "story",
        "road",
        "guest",
        "base",
        "heat",
        "aircon",
        "park",
        "pref",
        "furn",
    ]

    plotFeatures(features, theta)


if __name__ == "__main__":
    main()