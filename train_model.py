# ------------------------------
# train_model.py
# ------------------------------

# 1️⃣ Imports
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import os

# ------------------------------
# 2️⃣ Parameters
# ------------------------------
dataset_dir = "dataset"   # Folder that contains 'apple/' and 'burger/'
img_size = (224, 224)
batch_size = 8
epochs = 10

# ------------------------------
# 3️⃣ Data Generators (split + normalization)
# ------------------------------
train_datagen = ImageDataGenerator(rescale=1./255, validation_split=0.2)

train_generator = train_datagen.flow_from_directory(
    dataset_dir,
    target_size=img_size,
    batch_size=batch_size,
    class_mode="categorical",
    subset="training"
)

val_generator = train_datagen.flow_from_directory(
    dataset_dir,
    target_size=img_size,
    batch_size=batch_size,
    class_mode="categorical",
    subset="validation"
)

# Automatically detect number of classes
num_classes = len(train_generator.class_indices)
print(f"✅ Detected {num_classes} classes: {train_generator.class_indices}")

# ------------------------------
# 4️⃣ Build Model (MobileNetV2 Base)
# ------------------------------
base_model = MobileNetV2(weights="imagenet", include_top=False, input_shape=(224,224,3))

# Freeze base layers
for layer in base_model.layers:
    layer.trainable = False

# Add custom layers
x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(128, activation="relu")(x)
predictions = Dense(num_classes, activation="softmax")(x)

model = Model(inputs=base_model.input, outputs=predictions)

# ------------------------------
# 5️⃣ Compile Model
# ------------------------------
model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])

# ------------------------------
# 6️⃣ Train Model
# ------------------------------
model.fit(
    train_generator,
    validation_data=val_generator,
    epochs=epochs
)

# ------------------------------
# 7️⃣ Save Model
# ------------------------------
os.makedirs("models", exist_ok=True)
model.save("models/custom_food_model.h5")

print("\n🎉 Training complete! Model saved as 'models/custom_food_model.h5'")
