output_file = "all.dsq"
input_files = (
	["library/m_root.dsq"],
	["library/m_run.dsq", "run"],
	["library/m_back.dsq"],
	["library/m_side.dsq"],
	["library/m_crouch.dsq"],
	["library/m_crouchRun.dsq", "crouchRun"],
	["library/m_crouchBack.dsq", "crouchBack"],
	["library/m_crouchSide.dsq", "crouchSide"],
	["library/m_look.dsq"],
	["library/m_headSide.dsq"],
	["library/m_headup.dsq"],
	["library/m_standjump.dsq"],
	["library/m_fall.dsq"],
	["library/m_armAttack.dsq"],
	["library/m_armReadyLeft.dsq", "armReadyLeft"],
	["library/m_armReadyRight.dsq", "armReadyRight"],
	["library/m_armReadyBoth.dsq", "armReadyBoth"],
	["library/m_talk.dsq"],
	["library/m_sit.dsq", "sit"],
	["library/m_activate.dsq", "activate"],
	["library/death1.dsq", "death1"],
	["library/shortSwordIdle.dsq"],
	["library/shortSwordHit1.dsq"],
	["library/shortSwordHit2.dsq"],
	["library/shortSwordRush.dsq"],
	["library/shortSwordRushHit.dsq"],
	["library/shortSwordRushReceive.dsq"],
	["library/shortBowEquip.dsq"],
	["library/shortBowIdle.dsq"],
	["library/shortBowPull.dsq"],
	["library/shortBowFire.dsq"],
	["library/drinkpotion.dsq"],
	["library/dropitem.dsq"],
	["library/pick1h_swing.dsq"],
)

from DsqFile import DsqFile, Sequence

def include_dsq(dsq_out, name, rename=None):
	dsq_in = DsqFile()

	with open(name, "rb") as fd:
		dsq_in.read(fd)

	dsq_in.nodes_lower = [node.lower() for node in dsq_in.nodes]
	last_seq = None

	for seq in dsq_in.sequences:
		print("processing {} -> {}".format(name, seq.name))
		last_seq = Sequence()

		last_seq.name = seq.name
		last_seq.flags = seq.flags
		last_seq.numKeyframes = seq.numKeyframes
		last_seq.duration = seq.duration
		last_seq.priority = seq.priority
		last_seq.firstGroundFrame = len(dsq_out.ground_translations)
		last_seq.baseRotation = len(dsq_out.rotations)
		last_seq.baseTranslation = len(dsq_out.translations)
		if seq.flags & Sequence.UniformScale:
			scales_out = dsq_out.uniform_scales
			scales_in = dsq_in.uniform_scales
			last_seq.baseScale = len(scales_out)
		elif seq.flags & Sequence.AlignedScale:
			scales_out = dsq_out.aligned_scales
			scales_in = dsq_in.aligned_scales
			last_seq.baseScale = len(scales_out)
		elif seq.flags & Sequence.ArbitraryScale:
			raise Error("sequence combination ArbitraryScale not implemented")
		last_seq.firstTrigger = len(dsq_out.triggers)
		last_seq.toolBegin = seq.toolBegin

		last_seq.rotationMatters = [False] * len(dsq_out.nodes)
		last_seq.translationMatters = [False] * len(dsq_out.nodes)
		last_seq.scaleMatters = [False] * len(dsq_out.nodes)
		last_seq.decalMatters = [False] * len(dsq_out.nodes)
		last_seq.iflMatters = [False] * len(dsq_out.nodes)
		last_seq.visMatters = [False] * len(dsq_out.nodes)
		last_seq.frameMatters = [False] * len(dsq_out.nodes)
		last_seq.matFrameMatters = [False] * len(dsq_out.nodes)

		i_rotation = 0
		i_translation = 0
		i_scale = 0

		for i, node in enumerate(dsq_out.nodes):
			try:
				j = dsq_in.nodes_lower.index(node.lower())
			except ValueError:
				continue
			if j < len(seq.rotationMatters) and seq.rotationMatters[j]:
				last_seq.rotationMatters[i] = True
				for k in range(seq.numKeyframes):
					dsq_out.rotations.append(dsq_in.rotations[i_rotation * seq.numKeyframes + k])
				i_rotation += 1
			if j < len(seq.translationMatters) and seq.translationMatters[j]:
				last_seq.translationMatters[i] = True
				for k in range(seq.numKeyframes):
					dsq_out.translations.append(dsq_in.translations[i_translation * seq.numKeyframes + k])
				i_translation += 1
			if j < len(seq.scaleMatters) and seq.scaleMatters[j]:
				last_seq.scaleMatters[i] = True
				for k in range(seq.numKeyframes):
					scales_out.append(scales_in[i_scale * seq.numKeyframes + k])
				i_scale += 1

		dsq_out.sequences.append(last_seq)

	if last_seq != None and rename != None:
		last_seq.name = rename

dsq_out = DsqFile()

with open("NodeOrder.txt") as fd:
	dsq_out.nodes = fd.read().splitlines()

for input_file in input_files:
	if len(input_file) == 2:
		include_dsq(dsq_out, input_file[0], input_file[1])
	else:
		include_dsq(dsq_out, input_file[0])

with open(output_file, "wb") as fd:
	dsq_out.write(fd)
