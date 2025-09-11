# script to find correspondance points in image for homography transformation
#input: To be determined

#output: json file with atleast 4 correspondance points
#saved as correspondancePoints.json in the cache folder

#sample json output:
# Example of the expected JSON output format for correspondance points:
# {
#     "points": [
#         {
#             "yard": "50",
#             "hash": "close",
#             "x": 100,
#             "y": 100
#         },
#         {
#             "yard": "50",
#             "hash": "far",
#             "x": 100,
#             "y": 100
#         }
#     ]
# }

import cv2
import json
import os

def findCorrespondancePoints(image_path):
    """
    Find correspondence points in image for homography transformation
    
    Args:
        image_path: Path to reference image
    
    Returns:
        List of correspondence points
    """
    # TODO: Implement correspondence point detection logic
    pass

def main():
    """Main function for standalone execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Correspondence Points Module')
    parser.add_argument('--image', type=str, required=True, help='Path to reference image')
    parser.add_argument('--output', type=str, default='cache/correspondancePoints.json', 
                       help='Path to output JSON file')
    
    args = parser.parse_args()
    
    # TODO: Call findCorrespondancePoints function and save results
    pass

if __name__ == "__main__":
    main()