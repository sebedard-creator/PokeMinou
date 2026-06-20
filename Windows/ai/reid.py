import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import numpy as np
import logging

logger = logging.getLogger("ReID")

class CatReID:
    def __init__(self):
        logger.info("Chargement du modèle ResNet50 pour le ReID...")
        # Chargement d'un modèle ResNet50 pré-entraîné sur ImageNet
        # On supprime la dernière couche (classification) pour récupérer un vecteur de caractéristiques
        resnet = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
        self.model = torch.nn.Sequential(*list(resnet.children())[:-1])
        self.model.eval()
        
        # S'il y a un GPU (CUDA), on l'utilise, sinon CPU
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        
        # Transformations standards pour ResNet50
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def extract_features(self, image: Image.Image) -> np.ndarray:
        """Extrait un vecteur mathématique (embedding) d'une image recadrée de chat."""
        # S'assurer que l'image est en RGB
        image = image.convert('RGB')
        
        input_tensor = self.transform(image).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            features = self.model(input_tensor)
            
        # Aplatir et convertir en numpy
        embedding = features.squeeze().cpu().numpy()
        
        # Normalisation L2 du vecteur (recommandé pour Cosine Similarity)
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
            
        return embedding

    def cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calcule la similarité cosinus entre deux vecteurs (entre -1 et 1)."""
        if vec1 is None or vec2 is None:
            return 0.0
        return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))
