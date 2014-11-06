# -*- coding: utf-8 -*-

from src_util import *
import re

class LogSpec:
	def __init__ (self, argInPrints, argOutPrints = {}, returnPrint = None):
		self.argInPrints	= argInPrints
		self.argOutPrints	= argOutPrints
		self.returnPrint	= returnPrint

def enum (group):
	return lambda name: "get%sStr(%s)" % (group, name)

def pointer (size):
	return lambda name: "getPointerStr(%s, %s)" % (name, size)

def enumPointer (group, size):
	return lambda name: "getEnumPointerStr(%s, %s, get%sName)" % (name, size, group)

def textureUnit (name):
	return "getTextureUnitStr(%s)" % name

stringVal = lambda name: "getStringStr(%s)" % name

# Special rules for printing call arguments
CALL_LOG_SPECS = {
	"glActiveTexture":						LogSpec({0: textureUnit}),
	"glBeginQuery":							LogSpec({0: enum("QueryTarget")}),
	"glBeginTransformFeedback":				LogSpec({0: enum("PrimitiveType")}),
	"glBindBuffer":							LogSpec({0: enum("BufferTarget")}),
	"glBindBufferBase":						LogSpec({0: enum("BufferTarget")}),
	"glBindBufferRange":					LogSpec({0: enum("BufferTarget")}),
	"glBindFramebuffer":					LogSpec({0: enum("FramebufferTarget")}),
	"glBindRenderbuffer":					LogSpec({0: enum("FramebufferTarget")}),
	"glBindTexture":						LogSpec({0: enum("TextureTarget")}),
	"glBindTransformFeedback":				LogSpec({0: enum("TransformFeedbackTarget")}),
	"glBlendEquation":						LogSpec({0: enum("BlendEquation")}),
	"glBlendEquationSeparate":				LogSpec({0: enum("BlendEquation"), 1: enum("BlendEquation")}),
	"glBlendFunc":							LogSpec({0: enum("BlendFactor"), 1: enum("BlendFactor")}),
	"glBlendFuncSeparate":					LogSpec({0: enum("BlendFactor"), 1: enum("BlendFactor"), 2: enum("BlendFactor"), 3: enum("BlendFactor")}),
	"glBlitFramebuffer":					LogSpec({8: enum("BufferMask"), 9: enum("TextureFilter")}),
	"glBufferData":							LogSpec({0: enum("BufferTarget"), 3: enum("Usage")}),
	"glBufferSubData":						LogSpec({0: enum("BufferTarget")}),
	"glCheckFramebufferStatus":				LogSpec({0: enum("FramebufferTarget")}, returnPrint = enum("FramebufferStatus")),
	"glClear":								LogSpec({0: enum("BufferMask")}),
	"glClearBufferfv":						LogSpec({0: enum("Buffer")}),
	"glClearBufferfi":						LogSpec({0: enum("Buffer")}),
	"glClearBufferiv":						LogSpec({0: enum("Buffer")}),
	"glClearBufferuiv":						LogSpec({0: enum("Buffer")}),
	"glCompressedTexImage2D":				LogSpec({0: enum("TextureTarget"), 2: enum("PixelFormat")}),
	"glCompressedTexSubImage2D":			LogSpec({0: enum("TextureTarget"), 6: enum("PixelFormat")}),
	"glCopyTexImage1D":						LogSpec({0: enum("TextureTarget"), 2: enum("PixelFormat")}),
	"glCopyTexImage2D":						LogSpec({0: enum("TextureTarget"), 2: enum("PixelFormat")}),
	"glCreateShader":						LogSpec({0: enum("ShaderType")}),
	"glCullFace":							LogSpec({0: enum("Face")}),
	"glDeleteBuffers":						LogSpec({1: pointer(size = "n")}),
	"glDeleteFramebuffers":					LogSpec({1: pointer(size = "n")}),
	"glDeleteQueries":						LogSpec({1: pointer(size = "n")}),
	"glDeleteRenderbuffers":				LogSpec({1: pointer(size = "n")}),
	"glDeleteBuffers":						LogSpec({1: pointer(size = "n")}),
	"glDeleteTextures":						LogSpec({1: pointer(size = "n")}),
	"glDeleteVertexArrays":					LogSpec({1: pointer(size = "n")}),
	"glDepthFunc":							LogSpec({0: enum("CompareFunc")}),
	"glDisable":							LogSpec({0: enum("EnableCap")}),
	"glDrawArrays":							LogSpec({0: enum("PrimitiveType")}),
	"glDrawArraysInstanced":				LogSpec({0: enum("PrimitiveType")}),
	"glDrawBuffers":						LogSpec({1: enumPointer("DrawReadBuffer", size = "n")}),
	"glDrawElements":						LogSpec({0: enum("PrimitiveType"), 2: enum("Type")}),
	"glDrawElementsInstanced":				LogSpec({0: enum("PrimitiveType"), 2: enum("Type")}),
	"glDrawRangeElements":					LogSpec({0: enum("PrimitiveType"), 4: enum("Type")}),
	"glDrawArraysIndirect":					LogSpec({0: enum("PrimitiveType")}),
	"glDrawElementsIndirect":				LogSpec({0: enum("PrimitiveType"), 1: enum("Type")}),
	"glDrawElementsBaseVertex":				LogSpec({0: enum("PrimitiveType"), 2: enum("Type")}),
	"glDrawElementsInstancedBaseVertex":	LogSpec({0: enum("PrimitiveType"), 2: enum("Type")}),
	"glDrawRangeElementsBaseVertex":		LogSpec({0: enum("PrimitiveType"), 4: enum("Type")}),
	"glMultiDrawArrays":					LogSpec({0: enum("PrimitiveType")}),
	"glMultiDrawElements":					LogSpec({0: enum("PrimitiveType"), 2: enum("Type")}),
	"glMultiDrawElementsBaseVertex":		LogSpec({0: enum("PrimitiveType"), 2: enum("Type")}),
	"glEnable":								LogSpec({0: enum("EnableCap")}),
	"glEndQuery":							LogSpec({0: enum("QueryTarget")}),
	"glFramebufferRenderbuffer":			LogSpec({0: enum("FramebufferTarget"), 1: enum("FramebufferAttachment"), 2: enum("FramebufferTarget")}),
	"glFramebufferTexture2D":				LogSpec({0: enum("FramebufferTarget"), 1: enum("FramebufferAttachment"), 2: enum("TextureTarget")}),
	"glFramebufferTextureLayer":			LogSpec({0: enum("FramebufferTarget"), 1: enum("FramebufferAttachment")}),
	"glFramebufferTexture":					LogSpec({0: enum("FramebufferTarget"), 1: enum("FramebufferAttachment")}),
	"glFramebufferParameteri":				LogSpec({0: enum("FramebufferTarget"), 1: enum("FramebufferParameter")}),
	"glFrontFace":							LogSpec({0: enum("Winding")}),
	"glGenBuffers":							LogSpec({}, argOutPrints = {1: pointer(size = "n")}),
	"glGenerateMipmap":						LogSpec({0: enum("TextureTarget")}),
	"glGenFramebuffers":					LogSpec({}, argOutPrints = {1: pointer(size = "n")}),
	"glGenQueries":							LogSpec({}, argOutPrints = {1: pointer(size = "n")}),
	"glGenRenderbuffers":					LogSpec({}, argOutPrints = {1: pointer(size = "n")}),
	"glGenTextures":						LogSpec({}, argOutPrints = {1: pointer(size = "n")}),
	"glGenTransformFeedbacks":				LogSpec({}, argOutPrints = {1: pointer(size = "n")}),
	"glGenVertexArrays":					LogSpec({}, argOutPrints = {1: pointer(size = "n")}),
#	"glGetActiveAttrib":
	"glGetActiveUniform":					LogSpec({}, argOutPrints = {3: pointer(size = "1"), 4: pointer(size = "1"), 5: enumPointer("ShaderVarType", size = "1"), 6: stringVal}),
	"glGetActiveUniformsiv":				LogSpec({2: pointer(size = "uniformCount"), 3: enum("UniformParam")}, argOutPrints = {4: pointer(size = "uniformCount")}),
#	"glGetAttachedShaders":
	"glGetBooleanv":						LogSpec({0: enum("GettableState")}),
	"glGetBufferParameteriv":				LogSpec({0: enum("BufferTarget"), 1: enum("BufferQuery")}),
	"glGetBufferParameteri64v":				LogSpec({0: enum("BufferTarget"), 1: enum("BufferQuery")}),
	"glGetError":							LogSpec({}, returnPrint = enum("Error")),
	"glGetFloatv":							LogSpec({0: enum("GettableState")}),
	"glGetFramebufferAttachmentParameteriv":
		LogSpec(
			{
				0: enum("FramebufferTarget"),
				1: enum("FramebufferAttachment"),
				2: enum("FramebufferAttachmentParameter")
			},
			argOutPrints = {3: lambda name: "getFramebufferAttachmentParameterValueStr(pname, %s)" % name}),
	"glGetFramebufferParameteriv":			LogSpec({0: enum("FramebufferTarget"), 1: enum("FramebufferParameter")}),
	"glGetIntegerv":						LogSpec({0: enum("GettableState")}),
	"glGetInteger64v":						LogSpec({0: enum("GettableState")}),
	"glGetIntegeri_v":						LogSpec({0: enum("GettableIndexedState")}),
	"glGetInteger64i_v":					LogSpec({0: enum("GettableIndexedState")}),
	"glGetInternalformativ":				LogSpec({0: enum("InternalFormatTarget"), 1: enum("PixelFormat"), 2: enum("InternalFormatParameter")}, argOutPrints = {4: pointer(size = "bufSize")}),
	"glGetMultisamplefv":					LogSpec({0: enum("MultisampleParameter")}, argOutPrints = {2: pointer(size = "2")}),
	"glGetProgramiv":						LogSpec({1: enum("ProgramParam")}, argOutPrints = {2: pointer(size = "1")}),
#	"glGetProgramInfoLog":
	"glGetProgramPipelineiv":				LogSpec({1: enum("PipelineParam")}, argOutPrints = {2: pointer(size = "1")}),
	"glGetQueryiv":							LogSpec({0: enum("QueryTarget"), 1: enum("QueryParam")}, argOutPrints = {2: pointer(size = "1")}),
	"glGetQueryObjectiv":					LogSpec({1: enum("QueryObjectParam")}, argOutPrints = {2: pointer(size = "1")}),
	"glGetQueryObjectuiv":					LogSpec({1: enum("QueryObjectParam")}, argOutPrints = {2: pointer(size = "1")}),
	"glGetQueryObjecti64v":					LogSpec({1: enum("QueryObjectParam")}, argOutPrints = {2: pointer(size = "1")}),
	"glGetQueryObjectui64v":				LogSpec({1: enum("QueryObjectParam")}, argOutPrints = {2: pointer(size = "1")}),
	"glGetRenderbufferParameteriv":			LogSpec({0: enum("FramebufferTarget"), 1: enum("RenderbufferParameter")}),
	"glGetSamplerParameterfv":				LogSpec({1: enum("TextureParameter")}),
	"glGetSamplerParameteriv":				LogSpec({1: enum("TextureParameter")}),
	"glGetShaderiv":						LogSpec({1: enum("ShaderParam")}, argOutPrints = {2: pointer(size = "1")}),
#	"glGetShaderInfoLog":
	"glGetShaderPrecisionFormat":			LogSpec({0: enum("ShaderType"), 1: enum("PrecisionFormatType")}),
#	"glGetShaderSource":
	"glGetString":							LogSpec({0: enum("GettableString")}),
	"glGetStringi":							LogSpec({0: enum("GettableString")}),
	"glGetTexParameterfv":					LogSpec({0: enum("TextureTarget"), 1: enum("TextureParameter")}),
	"glGetTexParameteriv":					LogSpec({0: enum("TextureTarget"), 1: enum("TextureParameter")}),
	"glGetTexLevelParameterfv":				LogSpec({0: enum("TextureTarget"), 2: enum("TextureLevelParameter")}),
	"glGetTexLevelParameteriv":				LogSpec({0: enum("TextureTarget"), 2: enum("TextureLevelParameter")}),
#	"glGetUniformfv":
#	"glGetUniformiv":
	"glGetUniformIndices":					LogSpec({2: pointer(size = "uniformCount")}, argOutPrints = {3: pointer(size = "uniformCount")}),
	"glGetVertexAttribfv":					LogSpec({1: enum("VertexAttribParameterName")}, argOutPrints = {2: pointer(size = "(pname == GL_CURRENT_VERTEX_ATTRIB ? 4 : 1)")}),
	"glGetVertexAttribiv":					LogSpec({1: enum("VertexAttribParameterName")}, argOutPrints = {2: pointer(size = "(pname == GL_CURRENT_VERTEX_ATTRIB ? 4 : 1)")}),
	"glGetVertexAttribIiv":					LogSpec({1: enum("VertexAttribParameterName")}, argOutPrints = {2: pointer(size = "(pname == GL_CURRENT_VERTEX_ATTRIB ? 4 : 1)")}),
	"glGetVertexAttribIuv":					LogSpec({1: enum("VertexAttribParameterName")}, argOutPrints = {2: pointer(size = "(pname == GL_CURRENT_VERTEX_ATTRIB ? 4 : 1)")}),
#	"glGetVertexAttribPointerv":
	"glHint":								LogSpec({0: enum("Hint"), 1: enum("HintMode")}),
	"glIsEnabled":							LogSpec({0: enum("EnableCap")}),
	"glPixelStorei":						LogSpec({0: enum("PixelStoreParameter")}),
	"glReadBuffer":							LogSpec({0: enum("DrawReadBuffer")}),
	"glReadPixels":							LogSpec({4: enum("PixelFormat"), 5: enum("Type")}),
	"glRenderbufferStorage":				LogSpec({0: enum("FramebufferTarget"), 1: enum("PixelFormat")}),
	"glRenderbufferStorageMultisample":		LogSpec({0: enum("FramebufferTarget"), 2: enum("PixelFormat")}),
	"glStencilFunc":						LogSpec({0: enum("CompareFunc")}),
	"glStencilFuncSeparate":				LogSpec({0: enum("Face"), 1: enum("CompareFunc")}),
	"glStencilMaskSeparate":				LogSpec({0: enum("Face")}),
	"glStencilOp":							LogSpec({0: enum("StencilOp"), 1: enum("StencilOp"), 2: enum("StencilOp")}),
	"glStencilOpSeparate":					LogSpec({0: enum("Face"), 1: enum("StencilOp"), 2: enum("StencilOp"), 3: enum("StencilOp")}),
	"glTexImage1D":							LogSpec({0: enum("TextureTarget"), 2: enum("PixelFormat"), 5: enum("PixelFormat"), 6: enum("Type")}),
	"glTexImage2D":							LogSpec({0: enum("TextureTarget"), 2: enum("PixelFormat"), 6: enum("PixelFormat"), 7: enum("Type")}),
	"glTexImage2DMultisample":				LogSpec({0: enum("TextureTarget"), 2: enum("PixelFormat"), 5: enum("Boolean")}),
	"glTexImage3D":							LogSpec({0: enum("TextureTarget"), 2: enum("PixelFormat"), 7: enum("PixelFormat"), 8: enum("Type")}),
	"glTexStorage2D":						LogSpec({0: enum("TextureTarget"), 2: enum("PixelFormat")}),
	"glTexStorage3D":						LogSpec({0: enum("TextureTarget"), 2: enum("PixelFormat")}),
	"glTexStorage2DMultisample":			LogSpec({0: enum("TextureTarget"), 2: enum("PixelFormat"), 5: enum("Boolean")}),
	"glTexStorage3DMultisample":			LogSpec({0: enum("TextureTarget"), 2: enum("PixelFormat"), 6: enum("Boolean")}),
	# \todo [2012-03-08 pyry] Pointer values..
	"glTexParameterf":						LogSpec({0: enum("TextureTarget"), 1: enum("TextureParameter")}),
	"glTexParameterfv":						LogSpec({0: enum("TextureTarget"), 1: enum("TextureParameter")}),
	"glTexParameteri":						LogSpec({0: enum("TextureTarget"), 1: enum("TextureParameter"), 2: lambda name: "getTextureParameterValueStr(pname, %s)" % name}),
	"glTexParameteriv":						LogSpec({0: enum("TextureTarget"), 1: enum("TextureParameter")}),
	"glTexSubImage1D":						LogSpec({0: enum("TextureTarget"), 4: enum("PixelFormat"), 5: enum("Type")}),
	"glTexSubImage2D":						LogSpec({0: enum("TextureTarget"), 6: enum("PixelFormat"), 7: enum("Type")}),
	"glTexSubImage3D":						LogSpec({0: enum("TextureTarget"), 8: enum("PixelFormat"), 9: enum("Type")}),
	"glUniform1fv":							LogSpec({2: pointer(size = "(count * 1)")}),
	"glUniform1iv":							LogSpec({2: pointer(size = "(count * 1)")}),
	"glUniform1uiv":						LogSpec({2: pointer(size = "(count * 1)")}),
	"glUniform2fv":							LogSpec({2: pointer(size = "(count * 2)")}),
	"glUniform2iv":							LogSpec({2: pointer(size = "(count * 2)")}),
	"glUniform2uiv":						LogSpec({2: pointer(size = "(count * 2)")}),
	"glUniform3fv":							LogSpec({2: pointer(size = "(count * 3)")}),
	"glUniform3iv":							LogSpec({2: pointer(size = "(count * 3)")}),
	"glUniform3uiv":						LogSpec({2: pointer(size = "(count * 3)")}),
	"glUniform4fv":							LogSpec({2: pointer(size = "(count * 4)")}),
	"glUniform4iv":							LogSpec({2: pointer(size = "(count * 4)")}),
	"glUniform4uiv":						LogSpec({2: pointer(size = "(count * 4)")}),
	"glUniformMatrix2fv":					LogSpec({3: pointer(size = "(count * 2*2)")}),
	"glUniformMatrix3fv":					LogSpec({3: pointer(size = "(count * 3*3)")}),
	"glUniformMatrix4fv":					LogSpec({3: pointer(size = "(count * 4*4)")}),
	"glUniformMatrix2x3fv":					LogSpec({3: pointer(size = "(count * 2*3)")}),
	"glUniformMatrix2x4fv":					LogSpec({3: pointer(size = "(count * 2*4)")}),
	"glUniformMatrix3x2fv":					LogSpec({3: pointer(size = "(count * 3*2)")}),
	"glUniformMatrix3x4fv":					LogSpec({3: pointer(size = "(count * 3*4)")}),
	"glUniformMatrix4x2fv":					LogSpec({3: pointer(size = "(count * 4*2)")}),
	"glUniformMatrix4x3fv":					LogSpec({3: pointer(size = "(count * 4*3)")}),
	"glProgramUniform1fv":					LogSpec({3: pointer(size = "(count * 1)")}),
	"glProgramUniform1iv":					LogSpec({3: pointer(size = "(count * 1)")}),
	"glProgramUniform1uiv":					LogSpec({3: pointer(size = "(count * 1)")}),
	"glProgramUniform2fv":					LogSpec({3: pointer(size = "(count * 2)")}),
	"glProgramUniform2iv":					LogSpec({3: pointer(size = "(count * 2)")}),
	"glProgramUniform2uiv":					LogSpec({3: pointer(size = "(count * 2)")}),
	"glProgramUniform3fv":					LogSpec({3: pointer(size = "(count * 3)")}),
	"glProgramUniform3iv":					LogSpec({3: pointer(size = "(count * 3)")}),
	"glProgramUniform3uiv":					LogSpec({3: pointer(size = "(count * 3)")}),
	"glProgramUniform4fv":					LogSpec({3: pointer(size = "(count * 4)")}),
	"glProgramUniform4iv":					LogSpec({3: pointer(size = "(count * 4)")}),
	"glProgramUniform4uiv":					LogSpec({3: pointer(size = "(count * 4)")}),
	"glProgramUniformMatrix2fv":			LogSpec({4: pointer(size = "(count * 2*2)")}),
	"glProgramUniformMatrix3fv":			LogSpec({4: pointer(size = "(count * 3*3)")}),
	"glProgramUniformMatrix4fv":			LogSpec({4: pointer(size = "(count * 4*4)")}),
	"glProgramUniformMatrix2x3fv":			LogSpec({4: pointer(size = "(count * 2*3)")}),
	"glProgramUniformMatrix2x4fv":			LogSpec({4: pointer(size = "(count * 2*4)")}),
	"glProgramUniformMatrix3x2fv":			LogSpec({4: pointer(size = "(count * 3*2)")}),
	"glProgramUniformMatrix3x4fv":			LogSpec({4: pointer(size = "(count * 3*4)")}),
	"glProgramUniformMatrix4x3fv":			LogSpec({4: pointer(size = "(count * 4*3)")}),
	"glProgramUniformMatrix4x2fv":			LogSpec({4: pointer(size = "(count * 4*2)")}),
	"glProvokingVertex":					LogSpec({0: enum("ProvokingVertex")}),
	"glVertexAttrib1fv":					LogSpec({1: pointer(size = "1")}),
	"glVertexAttrib2fv":					LogSpec({1: pointer(size = "2")}),
	"glVertexAttrib3fv":					LogSpec({1: pointer(size = "3")}),
	"glVertexAttrib4fv":					LogSpec({1: pointer(size = "4")}),
	"glVertexAttrib1sv":					LogSpec({1: pointer(size = "1")}),
	"glVertexAttrib2sv":					LogSpec({1: pointer(size = "2")}),
	"glVertexAttrib3sv":					LogSpec({1: pointer(size = "3")}),
	"glVertexAttrib4sv":					LogSpec({1: pointer(size = "4")}),
	"glVertexAttrib1dv":					LogSpec({1: pointer(size = "1")}),
	"glVertexAttrib2dv":					LogSpec({1: pointer(size = "2")}),
	"glVertexAttrib3dv":					LogSpec({1: pointer(size = "3")}),
	"glVertexAttrib4dv":					LogSpec({1: pointer(size = "4")}),
	"glVertexAttrib4bv":					LogSpec({1: pointer(size = "4")}),
	"glVertexAttrib4iv":					LogSpec({1: pointer(size = "4")}),
	"glVertexAttrib4ubv":					LogSpec({1: pointer(size = "4")}),
	"glVertexAttrib4usv":					LogSpec({1: pointer(size = "4")}),
	"glVertexAttrib4uiv":					LogSpec({1: pointer(size = "4")}),
	"glVertexAttrib4Nbv":					LogSpec({1: pointer(size = "4")}),
	"glVertexAttrib4Nsv":					LogSpec({1: pointer(size = "4")}),
	"glVertexAttrib4Niv":					LogSpec({1: pointer(size = "4")}),
	"glVertexAttrib4Nubv":					LogSpec({1: pointer(size = "4")}),
	"glVertexAttrib4Nusv":					LogSpec({1: pointer(size = "4")}),
	"glVertexAttrib4Nuiv":					LogSpec({1: pointer(size = "4")}),
	"glVertexAttribI1iv":					LogSpec({1: pointer(size = "1")}),
	"glVertexAttribI2iv":					LogSpec({1: pointer(size = "2")}),
	"glVertexAttribI3iv":					LogSpec({1: pointer(size = "3")}),
	"glVertexAttribI4iv":					LogSpec({1: pointer(size = "4")}),
	"glVertexAttribI1uiv":					LogSpec({1: pointer(size = "1")}),
	"glVertexAttribI2uiv":					LogSpec({1: pointer(size = "2")}),
	"glVertexAttribI3uiv":					LogSpec({1: pointer(size = "3")}),
	"glVertexAttribI4uiv":					LogSpec({1: pointer(size = "4")}),
	"glVertexAttribI4bv":					LogSpec({1: pointer(size = "4")}),
	"glVertexAttribI4sv":					LogSpec({1: pointer(size = "4")}),
	"glVertexAttribI4ubv":					LogSpec({1: pointer(size = "4")}),
	"glVertexAttribI4usv":					LogSpec({1: pointer(size = "4")}),
	"glVertexAttribPointer":				LogSpec({2: enum("Type")}),
	"glVertexAttribIPointer":				LogSpec({2: enum("Type")}),
	"glVertexAttribFormat":					LogSpec({2: enum("Type")}),
	"glVertexAttribIFormat":				LogSpec({2: enum("Type")}),
	"glInvalidateFramebuffer":				LogSpec({0: enum("FramebufferTarget"), 2: enumPointer("InvalidateAttachment", "numAttachments")}),
	"glInvalidateSubFramebuffer":			LogSpec({0: enum("FramebufferTarget"), 2: enumPointer("InvalidateAttachment", "numAttachments")}),
	"glMapBufferRange":						LogSpec({0: enum("BufferTarget"), 3: enum("BufferMapFlags")}),
	"glUnmapBuffer":						LogSpec({0: enum("BufferTarget")}),
	"glFlushMappedBufferRange":				LogSpec({0: enum("BufferTarget")}),
	"glMemoryBarrier":						LogSpec({0: enum("MemoryBarrierFlags")}),
	"glBindImageTexture":					LogSpec({5: enum("ImageAccess"), 6: enum("PixelFormat")}),
	"glGetProgramResourceIndex":			LogSpec({1: enum("ProgramInterface")}),
	"glGetProgramResourceiv":				LogSpec({1: enum("ProgramInterface")}),
	"glDebugMessageInsert":					LogSpec({0: enum("DebugMessageSource"), 1: enum("DebugMessageType"), 3: enum("DebugMessageSeverity")}),
	"glDebugMessageControl":				LogSpec({0: enum("DebugMessageSource"), 1: enum("DebugMessageType"), 2: enum("DebugMessageSeverity"), 4: pointer(size = "(count)")}),
	"glPushDebugGroup":						LogSpec({0: enum("DebugMessageSource")}),
	"glTexBuffer":							LogSpec({0: enum("BufferTarget"), 1: enum("PixelFormat")}),
	"glTexBufferRange":						LogSpec({0: enum("BufferTarget"), 1: enum("PixelFormat")}),
}

def glwPrefix(string):
	return re.sub(r'\bGL', 'glw::GL', string)

def prefixedParams(command):
	if len(command.params) > 0:
		return ", ".join(glwPrefix(param.declaration) for param in command.params)
	else:
		return "void"

def commandLogWrapperMemberDecl (command):
	return "%s\t%s\t(%s);" % (glwPrefix(command.type), command.name, prefixedParams(command))

def getVarDefaultPrint (type, varName):
	if re.match(r'^const +(GLchar|GLubyte) *\*$', type):
		return "getStringStr(%s)" % varName
	elif re.match(r'(GLubyte|GLbyte|GLenum|GLushort|GLbitfield|\*)$', type):
		return "toHex(%s)" % varName
	elif type == 'GLboolean':
		return "getBooleanStr(%s)" % varName
	else:
		return varName

def commandLogWrapperMemberDef (command):
	src = ""
	try:
		logSpec = CALL_LOG_SPECS[command.name]
	except KeyError:
		logSpec = None

	src += "\n"
	src += "%s CallLogWrapper::%s (%s)\n{\n" % (glwPrefix(command.type), command.name, ", ".join(glwPrefix(p.declaration) for p in command.params))

	# Append paramemetrs
	callPrintItems = ["\"%s(\"" % command.name]
	for paramNdx, param in enumerate(command.params):
		if paramNdx > 0:
			callPrintItems.append("\", \"")

		if logSpec and paramNdx in logSpec.argInPrints:
			callPrintItems.append(logSpec.argInPrints[paramNdx](param.name))
		else:
			callPrintItems.append(getVarDefaultPrint(param.type, param.name))

	callPrintItems += ["\");\"", "TestLog::EndMessage"]

	src += "\tif (m_enableLog)\n"
	src += "\t\tm_log << TestLog::Message << %s;\n" % " << ".join(callPrintItems)

	callStr = "m_gl.%s(%s)" % (getFunctionMemberName(command.name), ", ".join([p.name for p in command.params]))

	isVoid	= command.type == 'void'
	if isVoid:
		src += "\t%s;\n" % callStr
	else:
		src += "\t%s returnValue = %s;\n" % (glwPrefix(command.type), callStr)

	if logSpec and len(logSpec.argOutPrints) > 0:
		# Print values returned in pointers
		src += "\tif (m_enableLog)\n\t{\n"

		for paramNdx, param in enumerate(command.params):
			if paramNdx in logSpec.argOutPrints:
				src += "\t\tm_log << TestLog::Message << \"// %s = \" << %s << TestLog::EndMessage;\n" % (param.name, logSpec.argOutPrints[paramNdx](param.name))

		src += "\t}\n"

	if not isVoid:
		# Print return value
		returnPrint = getVarDefaultPrint(command.type, "returnValue")
		if logSpec and logSpec.returnPrint:
			returnPrint = logSpec.returnPrint("returnValue")

		src += "\tif (m_enableLog)\n"
		src += "\t\tm_log << TestLog::Message << \"// \" << %s << \" returned\" << TestLog::EndMessage;\n" % returnPrint
		src += "\treturn returnValue;\n"

	src += "}"
	return src

def genCallLogWrapper (iface):
	genCommandList(iface, commandLogWrapperMemberDecl, OPENGL_DIR, "gluCallLogWrapperApi.inl", True)
	genCommandList(iface, commandLogWrapperMemberDef, OPENGL_DIR, "gluCallLogWrapper.inl", False)

if __name__ == "__main__":
	genCallLogWrapper(getHybridInterface())
