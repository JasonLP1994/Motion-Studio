// Person matte on a Mac, free and offline (macOS 12+), using Apple Vision's person segmentation.
// It keeps hands, arms and hair edges well. It does NOT keep things a person holds (a mic, a product).
// 1. Pull frames:  mkdir -p notes/frames/take && npx remotion ffmpeg -i inputs/take.mp4 notes/frames/take/%04d.jpg
// 2. Run:          swift mia-motion-graphics/scripts/person_matte.swift notes/frames/take notes/mattes/take
// Output: one grey PNG per frame (white = person), same name number and size as the frame.
import Foundation
import Vision
import CoreImage
import ImageIO
import UniformTypeIdentifiers

let args = CommandLine.arguments
guard args.count >= 3 else { print("usage: swift person_matte.swift <frames_dir> <out_dir>"); exit(1) }
let src = URL(fileURLWithPath: args[1]), out = URL(fileURLWithPath: args[2])
try? FileManager.default.createDirectory(at: out, withIntermediateDirectories: true)
let files = try FileManager.default.contentsOfDirectory(atPath: src.path)
  .filter { $0.lowercased().hasSuffix(".jpg") || $0.lowercased().hasSuffix(".png") }.sorted()
let ctx = CIContext(options: [.workingColorSpace: NSNull()])
let grey = CGColorSpaceCreateDeviceGray()
let request = VNGeneratePersonSegmentationRequest()
request.qualityLevel = .accurate
request.outputPixelFormat = kCVPixelFormatType_OneComponent8

var done = 0
for name in files {
  let url = src.appendingPathComponent(name)
  guard let isrc = CGImageSourceCreateWithURL(url as CFURL, nil),
        let cg = CGImageSourceCreateImageAtIndex(isrc, 0, nil) else { print("skip \(name)"); continue }
  try VNImageRequestHandler(cgImage: cg, options: [:]).perform([request])
  guard let mask = request.results?.first?.pixelBuffer else { print("no person in \(name)"); continue }
  var m = CIImage(cvPixelBuffer: mask)
  let sx = CGFloat(cg.width) / m.extent.width, sy = CGFloat(cg.height) / m.extent.height
  m = m.applyingFilter("CILanczosScaleTransform", parameters: [kCIInputScaleKey: sy, kCIInputAspectRatioKey: sx / sy])
  guard let outCG = ctx.createCGImage(m, from: CGRect(x: 0, y: 0, width: cg.width, height: cg.height), format: .L8, colorSpace: grey) else { continue }
  let base = (name as NSString).deletingPathExtension
  guard let d = CGImageDestinationCreateWithURL(out.appendingPathComponent(base + ".png") as CFURL, UTType.png.identifier as CFString, 1, nil) else { continue }
  CGImageDestinationAddImage(d, outCG, nil); CGImageDestinationFinalize(d)
  done += 1
  if done % 100 == 0 { print("\(done) frames") }
}
print("done: \(done) mattes in \(out.path)")
