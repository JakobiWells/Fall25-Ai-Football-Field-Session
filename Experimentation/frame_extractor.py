import cv2
import os
from pathlib import Path

# This is a simple script to extract frames from a video.


def extract_frames_from_video(video_path, output_folder, fps=None):
    """
    Extract frames from a single video.
    
    Args:
        video_path (str or Path): Path to the video file.
        output_folder (str): Folder to save frames.
        fps (float, optional): If set, only save this many frames per second.
    """
    os.makedirs(output_folder, exist_ok=True)
    cap = cv2.VideoCapture(str(video_path))
    video_fps = cap.get(cv2.CAP_PROP_FPS)
    frame_num = 0
    saved_frame_num = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # If fps is set, skip frames to match desired fps
        if fps is not None:
            if frame_num % int(video_fps / fps) != 0:
                frame_num += 1
                continue

        cv2.imwrite(f'{output_folder}/frame_{saved_frame_num:04d}.jpg', frame)
        saved_frame_num += 1
        frame_num += 1

    cap.release()
    print(f'{saved_frame_num} frames extracted from {video_path.name} into {output_folder}')

def extract_frames_from_folder(video_folder, output_root='frames', fps=None):
    """
    Loop through all mp4 files in a folder and extract frames.
    
    Args:
        video_folder (str): Folder containing mp4 videos.
        output_root (str): Root folder to save frames.
        fps (float, optional): Desired frames per second for output.
    """
    os.makedirs(output_root, exist_ok=True)
    for video_file in Path(video_folder).glob('*.mp4'):
        video_name = video_file.stem
        output_folder = os.path.join(output_root, video_name)
        extract_frames_from_video(video_file, output_folder, fps=fps)

# Example usage:
extract_frames_from_folder('football_film', output_root='testing_data/frames', fps=None)  # set fps=5 to downsample