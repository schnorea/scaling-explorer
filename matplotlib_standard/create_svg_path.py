#!/usr/bin/env python3
"""
SVG Path Generator using svgwrite
Creates an SVG file from a given path description.
"""

import svgwrite

def parse_path_to_coordinates(path_data):
    """
    Parse SVG path data and convert to absolute x,y coordinates
    """
    # Clean up the path data
    clean_path = ' '.join(path_data.split())
    
    # Split into tokens
    tokens = clean_path.replace(',', ' ').split()
    
    coordinates = []
    current_x, current_y = 0, 0
    i = 0
    
    while i < len(tokens):
        command = tokens[i]
        
        if command == 'm':  # relative moveto
            current_x += float(tokens[i+1])
            current_y += float(tokens[i+2])
            coordinates.append((current_x, current_y))
            i += 3
            
        elif command == 'h':  # relative horizontal line
            # Process all the horizontal values that follow
            i += 1
            while i < len(tokens) and not tokens[i].isalpha():
                current_x += float(tokens[i])
                coordinates.append((current_x, current_y))
                i += 1
                
        elif command == 'v':  # relative vertical line
            i += 1
            while i < len(tokens) and not tokens[i].isalpha():
                current_y += float(tokens[i])
                coordinates.append((current_x, current_y))
                i += 1
            
        elif command == 'H':  # absolute horizontal line
            # Process all the horizontal values that follow
            i += 1
            while i < len(tokens) and not tokens[i].isalpha():
                current_x = float(tokens[i])
                coordinates.append((current_x, current_y))
                i += 1
                
        elif command == 'Z' or command == 'z':  # close path
            if coordinates:  # Close back to first point
                coordinates.append(coordinates[0])
            i += 1
        else:
            i += 1
    
    return coordinates

def create_svg_from_path():
    # Path data from the user
    path_data = """m 2.9435074,177.49356
h 12.7674686 12.767468 12.767468 12.767469 12.767468 12.767468 12.767468 12.767465 12.76747 12.76747 12.76747 12.76747 12.76747 12.76746 12.76747 12.76747
v 5.59267
H 194.45553 181.68806 168.9206 156.15313 143.38566 130.61819 117.85072 105.08325 92.315785 79.548317 66.780849 54.013381 41.245912 28.478444 15.710976 2.9435074
Z"""
    
    # Parse path to coordinates
    coordinates = parse_path_to_coordinates(path_data)
    
    # Print the coordinates
    print("Path converted to x,y coordinates:")
    print("=" * 40)
    for i, (x, y) in enumerate(coordinates):
        print(f"Point {i+1:2d}: ({x:10.6f}, {y:10.6f})")
    
    print(f"\nTotal points: {len(coordinates)}")
    
    # Create polyline path from coordinates
    polyline_points = " ".join([f"{x},{y}" for x, y in coordinates])
    
    # Clean up the original path data
    clean_path = ' '.join(path_data.split())
    
    # Create SVG drawing with appropriate size
    dwg = svgwrite.Drawing('generated_path.svg', size=('210px', '200px'))
    
    # Add a white background
    dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill='white'))
    
    # Create the original path element
    original_path = dwg.path(
        d=clean_path,
        stroke='blue',
        stroke_width='2',
        fill='lightblue',
        fill_opacity='0.5'
    )
    dwg.add(original_path)
    
    # Create a polyline from the coordinates for comparison
    polyline = dwg.polyline(
        points=polyline_points,
        stroke='red',
        stroke_width='1',
        fill='none',
        stroke_dasharray='3,3'
    )
    dwg.add(polyline)
    
    # Add coordinate points as small circles
    for i, (x, y) in enumerate(coordinates[::4]):  # Show every 4th point to avoid clutter
        circle = dwg.circle(center=(x, y), r=1.5, fill='red', stroke='darkred', stroke_width='0.5')
        dwg.add(circle)
        
        # Add point labels for first few points
        if i < 5:
            text = dwg.text(f'P{i*4+1}', insert=(x+3, y-3), 
                           font_family='Arial', font_size='8', fill='darkred')
            dwg.add(text)
    
    # Add legend
    legend_y = 15
    dwg.add(dwg.text('Legend:', insert=(10, legend_y), 
                     font_family='Arial', font_size='10', fill='black', font_weight='bold'))
    dwg.add(dwg.line(start=(10, legend_y+10), end=(30, legend_y+10), 
                     stroke='blue', stroke_width='2'))
    dwg.add(dwg.text('Original Path', insert=(35, legend_y+13), 
                     font_family='Arial', font_size='8', fill='blue'))
    dwg.add(dwg.line(start=(10, legend_y+20), end=(30, legend_y+20), 
                     stroke='red', stroke_width='1', stroke_dasharray='3,3'))
    dwg.add(dwg.text('Coordinate Points', insert=(35, legend_y+23), 
                     font_family='Arial', font_size='8', fill='red'))
    
    # Save the SVG file
    dwg.save()
    print(f"\nSVG file 'generated_path.svg' created with both representations!")
    
    return coordinates

def main():
    """Main function to execute the script"""
    try:
        coordinates = create_svg_from_path()
        
        # Option to save coordinates to a text file
        with open('path_coordinates.txt', 'w') as f:
            f.write("Path Coordinates (x, y)\n")
            f.write("=" * 25 + "\n")
            for i, (x, y) in enumerate(coordinates):
                f.write(f"Point {i+1:2d}: ({x:10.6f}, {y:10.6f})\n")
        
        print("\nCoordinates also saved to 'path_coordinates.txt'")
        
    except Exception as e:
        print(f"Error creating SVG: {e}")

if __name__ == "__main__":
    main()